"""
CDT.PY by Javier Garcia

Simple tool to create and add content to Amstrad CDT files.
INFO about the CDT file format can be read here:
https://www.cpcwiki.eu/index.php/Format:CDT_tape_image_file_format

Details about how information in stored in real tapes can be
found in the Firmware guide (chapter 8):
https://archive.org/details/SOFT968TheAmstrad6128FirmwareManual

As per de documentation, timings are expected as Z80 clock ticks (T states)
unless otherwise stated. 1 T state = (1/4000000)s (CPC Z80 ran at 4 Mhz)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in its version 3.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__ = 'Javier "Dwayne Hicks" Garcia'
__version__ = "1.0"

import sys
import argparse
import math
import json
import os
from typing import List, Union

AMSDOS_BAS_TYPE = 0
AMSDOS_PROTECTED_TYPE = 1
AMSDOS_BIN_TYPE = 2

DEF_DATA_BLOCK_SZ = 2048  # max size for a data block (2K)
DEF_DATA_SEGMENT_SZ = 256
DEF_DATA_TRAIL = [0xFF, 0xFF, 0xFF, 0xFF]
DEF_WRITE_SPEED = 2000  # 1000 is another common value
DEF_PAUSE_HEADER = 15  # ms
DEF_PAUSE_DATA = 2560  # ms
DEF_PAUSE_FILE = 12000  # ms


class OutputFormatter:
    """
    Formats CDT information as Markdown tables or JSON.
    """

    def __init__(self, format_type="markdown"):
        self.format_type = format_type

    def format_cat(self, cdt_file, cdt):
        """Format the output of 'cat' command."""
        if self.format_type == "json":
            return self._format_cat_json(cdt_file, cdt)
        else:
            return self._format_cat_markdown(cdt_file, cdt)

    def _format_cat_markdown(self, cdt_file, cdt):
        """Format cat output as Markdown table."""
        output = []
        output.append(f"CDT: {cdt_file}")
        output.append(f"Version: {cdt.header.major}.{cdt.header.minor}")
        output.append("")
        output.append(
            "| Block # | Type           | Size   | Details                          |"
        )
        output.append(
            "|---------|----------------|--------|----------------------------------|"
        )

        pending_header = None
        for idx, block in enumerate(cdt.blocks, 1):
            block_type = self._get_block_type_name(block)
            size_info = self._get_block_size_info(block)
            header_obj = self._extract_data_header(block)
            if header_obj:
                pending_header = header_obj
                details = self._format_header_summary(header_obj)
            elif pending_header and self._is_cpc_data_block(block):
                details = f"Data: {pending_header.block_sz} bytes"
                pending_header = None
            else:
                details = self._get_block_details(block)
            output.append(
                f"| {idx:<7} | {block_type:<14} | {size_info:<6} | {details:<32} |"
            )

        return "\n".join(output)

    def _format_cat_json(self, cdt_file, cdt):
        """Format cat output as JSON."""
        data = {
            "cdt_file": cdt_file,
            "version": f"{cdt.header.major}.{cdt.header.minor}",
            "blocks": [],
        }

        pending_header = None
        for idx, block in enumerate(cdt.blocks, 1):
            block_data = {
                "index": idx,
                "type": self._get_block_type_name(block),
                "id": hex(block.ID),
            }

            # Add type-specific fields
            if isinstance(block, BlockPause):
                block_data["pause_ms"] = block.pause
            elif isinstance(block, (BlockTurboSpeed, BlockPureData, BlockNormalSpeed)):
                block_data["data_bytes"] = len(block.data)
                if hasattr(block, "pause"):
                    block_data["pause_ms"] = block.pause
                header_obj = self._extract_data_header(block)
                if header_obj:
                    pending_header = header_obj
                    block_data["header"] = {
                        "filename": header_obj.filename.strip("\x00"),
                        "type": self._get_file_type_name(header_obj.type),
                        "block_id": header_obj.block_id,
                        "first_block": header_obj.first_block == 0xFF,
                        "last_block": header_obj.last_block == 0xFF,
                        "load_addr": hex(header_obj.addr_load),
                        "start_addr": hex(header_obj.addr_start),
                        "length": header_obj.length,
                    }
                elif pending_header and self._is_cpc_data_block(block):
                    block_data["payload_bytes"] = pending_header.block_sz
                    pending_header = None
                else:
                    payload = getattr(block, "payload_size", None)
                    if isinstance(block, BlockNormalSpeed):
                        payload = payload or max(0, len(block.data) - 2)
                        block_data["payload_bytes"] = payload
                    elif payload:
                        block_data["payload_bytes"] = payload

            data["blocks"].append(block_data)

        return json.dumps(data, indent=2)

    def _get_block_type_name(self, block):
        """Get human-readable block type name."""
        if isinstance(block, BlockPause):
            return "Pause"
        elif isinstance(block, BlockTurboSpeed):
            return "Turbo Speed"
        elif isinstance(block, BlockPureData):
            return "Pure Data"
        elif isinstance(block, BlockNormalSpeed):
            return "Normal Speed"
        elif isinstance(block, BlockGroupStart):
            return "Group Start"
        elif isinstance(block, BlockGroupEnd):
            return "Group End"
        else:
            return f"Block 0x{block.ID:02X}"

    def _get_block_size_info(self, block):
        """Get size information for block."""
        if isinstance(block, BlockPause):
            return f"{block.pause}ms"
        elif isinstance(block, (BlockTurboSpeed, BlockPureData, BlockNormalSpeed)):
            return f"{len(block.data)}B"
        else:
            return "-"

    def _get_block_details(self, block):
        """Get detailed information for block."""
        if isinstance(block, BlockPause):
            if block.pause == DEF_PAUSE_FILE:
                return "File end pause"
            elif block.pause == DEF_PAUSE_HEADER:
                return "Header pause"
            elif block.pause == DEF_PAUSE_DATA:
                return "Data pause"
            else:
                return f"Pause {block.pause}ms"
        elif isinstance(block, (BlockTurboSpeed, BlockPureData, BlockNormalSpeed)):
            if isinstance(block, BlockNormalSpeed):
                payload = getattr(block, "payload_size", None)
                if not payload:
                    payload = max(0, len(block.data) - 2)
                return f"Spectrum data ({payload} bytes)"
            header = self._extract_data_header(block)
            if header:
                return self._format_header_summary(header)
            elif len(block.data) > 0 and block.data[0] == 0x16:
                payload = getattr(block, "payload_size", None)
                if payload is None or payload == 0:
                    return f"Raw data block (encoded {len(block.data)} bytes)"
                return f"Data: {payload} bytes"
            else:
                return "Unknown data"
        else:
            return ""

    def _get_file_type_name(self, type_code):
        """Convert file type code to name."""
        if type_code == DataHeader.FT_BAS:
            return "BAS"
        elif type_code == DataHeader.FT_BIN:
            return "BIN"
        elif type_code == DataHeader.FT_ASCII:
            return "ASCII"
        else:
            return f"0x{type_code:02X}"

    def _extract_data_header(self, block):
        """Return DataHeader instance if block encodes one."""
        if isinstance(block, (BlockTurboSpeed, BlockPureData)):
            if len(block.data) > 0 and block.data[0] == DataHeader.SYNC:
                try:
                    header = DataHeader()
                    header.set(block.data[1:])
                    return header
                except Exception:
                    return None
        return None

    def _format_header_summary(self, header):
        filename = header.filename.strip("\x00")
        file_type = self._get_file_type_name(header.type)
        addr = f" @ {hex(header.addr_load)}" if header.type != DataHeader.FT_BAS else ""
        return f"Header: {filename} ({file_type}){addr}"

    def _is_cpc_data_block(self, block):
        return (
            isinstance(block, (BlockTurboSpeed, BlockPureData))
            and len(block.data) > 0
            and block.data[0] == 0x16
        )

    def format_check(self, cdt_file, success, errors=None):
        """Format the output of 'check' command."""
        if self.format_type == "json":
            data = {
                "file": cdt_file,
                "valid": success,
                "errors": errors if errors else [],
            }
            return json.dumps(data, indent=2)
        else:
            if success:
                return f"[OK] {cdt_file}: Valid CDT format"
            else:
                output = [f"[ERROR] {cdt_file}: Invalid CDT format"]
                if errors:
                    for err in errors:
                        output.append(f"- {err}")
                return "\n".join(output)


def AUX_GET_CRC(data):
    """
    Auxiliary function that calculates the CRC on 256 bytes of data
    using CRC-16-CCITT Polynomial: X^16+X^12+X^5+1 and an initial
    seed 0xFFFF
    """
    crc = 0xFFFF
    for i in range(0, 256):
        k = crc >> 8 ^ data[i]
        k = k ^ k >> 4
        crc = crc << 8 ^ k << 12 ^ k << 5 ^ k
        crc = crc & 0xFFFF
    crc = crc ^ 0xFFFF
    return crc


def AUX_BAUDS2PULSE(speed):
    # Let's calculate de pulse time in nanoseconds following the
    # firmware guide
    pulse = 333333 / speed
    # following the CDT format guide lets calculate the pulse
    # as CPU cycles (aka T steps): (pulse / 1000000) * 3500000
    return math.ceil(pulse * 3.5)


class FormatError(Exception):
    """
    Raised when procesing a file and its format is not the expected one.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class CDTHeader:
    """
    Encapsulates the header of a CDT file. It compromises the first 10 bytes.
    0       "ZXTape!"
    7       0x1A
    8       Major version number
    9       Minor version number
    """

    def __init__(self):
        self.title = "ZXTape!"
        self.major = 1
        self.minor = 13

    def compose(self):
        # Total size of 10 bytes
        header = bytearray(self.title.encode("utf-8"))
        header.extend(b"\x1a")
        header.extend(self.major.to_bytes(1, "little"))
        header.extend(self.minor.to_bytes(1, "little"))
        return header

    def set(self, content):
        if len(content) < 10:
            raise FormatError("header size is less than 10 bytes")
        self.title = content[0:7].decode("utf-8")
        self.major = int(content[8])
        self.minor = int(content[9])
        return content[10:]

    def check(self):
        if "ZXTape!" not in self.title:
            raise FormatError("CDT header title doesn't contain 'ZXTape!' text")

    def dump(self):
        print("CDT HEADER title:", self.title, "version:", self.major, ".", self.minor)


class DataHeader:
    """
    Encapsulates de header for CDT data blocks. It starts with
    the sync byte 0x2C

    Header (28 bytes):
        00  16   Filename (padded with 0x00)
    10   1   block ID (1,2,3...)
        11   1   Last block? (0xFF or 0x00)
    12   1   Type (0x00: BAS, 0x01: Protected, 0x02: BIN, 0x16: ASCII)
    13   2   Block size
    15   2   Start + past blocks (loading address for this block)
    17   1   First block? (0xFF or 0x00)
    19   2   Length
    1B   2   call address
    """

    FT_BAS = 0x00
    FT_BIN = 0x02
    FT_ASCII = 0x16
    SYNC = 0x2C

    def __init__(self):
        self.filename = "UNNAMED"
        self.block_id = 1
        self.last_block = 0x00
        self.type = self.FT_BIN
        self.block_sz = 1 + 256 + 2 + 4  # segment sync + size + CRC + trail
        self.addr_load = 0
        self.first_block = 0xFF
        self.length = 0
        self.addr_start = 0x4000

    def set(self, content):
        self.filename = content[0:16].decode("utf-8")
        self.block_id = int(content[16])
        self.last_block = int(content[17])
        self.type = int(content[18])
        self.block_sz = int.from_bytes(content[19:21], "little")
        self.addr_load = int.from_bytes(content[21:23], "little")
        self.first_block = int(content[23])
        self.length = int.from_bytes(content[24:26], "little")
        self.addr_start = int.from_bytes(content[26:28], "little")
        # Segments are always of 256 bytes plus CRC (2) and trail (4)
        return content[256 + 2 + 4 :]

    def compose(self):
        content = bytearray()
        content.extend(b"\x2c")  # sync byte
        name = bytearray(self.filename[0:16].encode("utf-8"))
        name.extend(0x00 for i in range(len(name), 16))
        content.extend(name)
        content.extend(self.block_id.to_bytes(1, "little"))
        content.extend(self.last_block.to_bytes(1, "little"))
        content.extend(self.type.to_bytes(1, "little"))
        content.extend(self.block_sz.to_bytes(2, "little"))
        content.extend(self.addr_load.to_bytes(2, "little"))
        content.extend(self.first_block.to_bytes(1, "little"))
        content.extend(self.length.to_bytes(2, "little"))
        content.extend(self.addr_start.to_bytes(2, "little"))
        # segment must be of 256 bytes plus the sync byte
        content.extend(0x00 for i in range(len(content), 256 + 1))
        # but CRC only on data
        crc = AUX_GET_CRC(content[1:])
        content.extend(crc.to_bytes(2, "big"))  # !!! here MSB first
        content.extend(b"\xff\xff\xff\xff")  # trail
        return content

    def dump(self):
        print(
            "Name:",
            self.filename.encode("utf-8"),
            "type:",
            hex(self.type),
            "Number:",
            self.block_id,
        )
        print(
            "Size:",
            self.block_sz,
            "First:",
            hex(self.first_block),
            "Last:",
            hex(self.last_block),
        )
        print(
            "Load Addr:",
            hex(self.addr_load),
            "Call addr:",
            hex(self.addr_start),
            "Length:",
            self.length,
        )

    def check(self):
        pass


class BlockNormalSpeed:
    """
    00 2  Pause After this block in milliseconds (ms)
    02 2  Length of following data
    04 x  Data
    """

    ID = 0x10

    def __init__(self, pause=DEF_PAUSE_DATA):
        self.pause = pause
        self.data = bytearray()
        self.payload_size = 0

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(self.pause.to_bytes(2, "little"))
        content.extend(len(self.data).to_bytes(2, "little"))
        content.extend(self.data)
        return content

    def set(self, content):
        self.pause = int.from_bytes(content[0:2], "little")
        sz = int.from_bytes(content[2:4], "little")
        self.data = content[4 : 4 + sz]
        return content[4 + sz :]

    def dump(self):
        print("Data block of standard speed (id 0x10), data (bytes)", len(self.data))

    def check(self):
        pass


class BlockTurboSpeed:
    """
    00 2  Length of PILOT pulse
    02 2  Length of SYNC First pulse
    04 2  Length of SYNC Second pulse
    06 2  Length of ZERO bit pulse
    08 2  Length of ONE bit pulse
    0A 2  Length of PILOT tone (in PILOT pulses)
    0C 1  Used bits in last byte (other bits should be 0)
    0D 2  Pause After this block in milliseconds (ms)
    0F 3  Length of following data
    12 x  Data; format is as for TAP (MSb first)

    All lengths are given in T states:
    Pilot pulse, length  Sync1    Sync2    Bit-0    Bit-1
    ------------------------------------------------------
      Bit-1       4096   Bit-0    Bit-0      *        *

    * Amstrad CPC ROM Load/Save routine can use variable speed for loading,
    so the Bit-1 pulse must be read from the Pilot Tone and Bit-0 can be read
    from the Sync pulses, and is always half the size of Bit-1.
    The speed can vary from 1000 to 2000 baud.
    """

    ID = 0x11

    def __init__(self, speed=DEF_WRITE_SPEED, pause=DEF_PAUSE_DATA):
        bit0 = AUX_BAUDS2PULSE(speed)
        bit1 = bit0 * 2
        self.pilot_len = bit1
        self.sync1_len = bit0
        self.sync2_len = bit0
        self.zero_len = bit0
        self.one_len = bit1
        self.ppulses_count = 4096
        self.used_bits = 8
        self.pause = pause
        self.data = bytearray()
        self.payload_size = 0

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(self.pilot_len.to_bytes(2, "little"))
        content.extend(self.sync1_len.to_bytes(2, "little"))
        content.extend(self.sync2_len.to_bytes(2, "little"))
        content.extend(self.zero_len.to_bytes(2, "little"))
        content.extend(self.one_len.to_bytes(2, "little"))
        content.extend(self.ppulses_count.to_bytes(2, "little"))
        content.extend(self.used_bits.to_bytes(1, "little"))
        content.extend(self.pause.to_bytes(2, "little"))
        content.extend(len(self.data).to_bytes(3, "little"))
        content.extend(self.data)
        return content

    def set(self, content):
        self.pilot_len = int.from_bytes(content[0:2], "little")
        self.sync1_len = int.from_bytes(content[2:4], "little")
        self.sync2_len = int.from_bytes(content[4:6], "little")
        self.zero_len = int.from_bytes(content[6:8], "little")
        self.one_len = int.from_bytes(content[8:10], "little")
        self.ppulses_count = int.from_bytes(content[10:12], "little")
        self.used_bits = content[12]
        self.pause = int.from_bytes(content[13:15], "little")
        sz = int.from_bytes(content[15:18], "little")
        self.data = content[18 : 18 + sz]
        return content[18 + sz :]

    def dump(self):
        print("Data block of turbo speed (id 0x11), data block (bytes)", len(self.data))
        print(
            "Lenghts: pilot %d sync1 %d sync2 %d zero %d one %d pulses %d pause %d"
            % (
                self.pilot_len,
                self.sync1_len,
                self.sync2_len,
                self.zero_len,
                self.one_len,
                self.ppulses_count,
                self.pause,
            )
        )
        if self.data[0] == 0x2C:
            header = DataHeader()
            header.set(self.data[1:])
            header.dump()
        elif self.data[0] == 0x16:
            print("Data block with 0x16 sync code")
        else:
            print("Uknown sync code:", hex(self.data[0]))
        print("")

    def check(self):
        pass


class BlockPureTone:
    """
    00 2  Length of pulse in T-States
    02 2  Number of pulses
    """

    ID = 0x12

    def __init__(self):
        self.length = 0
        self.pulses = 0

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(self.length.to_bytes(2, "little"))
        content.extend(self.pulses.to_bytes(2, "little"))
        return content

    def set(self, content):
        self.length = int.from_bytes(content[0:2], "little")
        self.pulses = int.from_bytes(content[2:4], "little")
        return content[4:]

    def dump(self):
        print(
            "Pure tone (id 0x12), pulse length:",
            self.length,
            "number of pulses:",
            self.pulses,
        )

    def check(self):
        pass


class BlockDifferentPulses:
    """
    00 1  Number of pulses
    01 2  Length of first pulse in T-States
    03 2  Length of second pulse...
    .. .  etc.
    - Length: [00]*02+01
    """

    ID = 0x13

    def __init__(self):
        self.lengths = []

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(len(self.lengths).to_bytes(1, "little"))
        for length in self.lengths:
            content.extend(length.to_bytes(2, "little"))
        return content

    def set(self, content):
        pulses = int(content[0])
        self.lengths = []
        for i in range(0, pulses):
            value = int.from_bytes(content[i * 2 + 1 : (i + 1) * 2 + 1], "little")
            self.lengths.append(value)
        return content[pulses * 2 + 1 :]

    def dump(self):
        print("Different pulses (id 0x13), number of pulses:", len(self.lengths))

    def check(self):
        pass


class BlockPureData:
    """
    00 2  Length of ZERO bit pulse
    02 2  Length of ONE bit pulse
    04 1  Used bits in LAST Byte
    05 2  Pause after this block in milliseconds (ms)
    07 3  Length of following data
    0A x  Data (MSb first)
    """

    ID = 0x14

    def __init__(self, speed=DEF_WRITE_SPEED, pause=DEF_PAUSE_DATA):
        self.zerop = AUX_BAUDS2PULSE(speed)
        self.onep = self.zerop * 2
        self.used = 8
        self.pause = pause
        self.data = bytearray()
        self.payload_size = 0

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(self.zerop.to_bytes(2, "little"))
        content.extend(self.onep.to_bytes(2, "little"))
        content.extend(self.used.to_bytes(1, "little"))
        content.extend(self.pause.to_bytes(2, "little"))
        content.extend(len(self.data).to_bytes(3, "little"))
        content.extend(self.data)
        return content

    def set(self, content):
        self.zerop = int.from_bytes(content[0:2], "little")
        self.onep = int.from_bytes(content[2:4], "little")
        self.used = int(content[4])
        self.pause = int.from_bytes(content[5:7], "little")
        sz = int.from_bytes(content[7:10], "little")
        self.data = content[10 : 10 + sz]
        return content[10 + sz :]

    def dump(self):
        print("Pure data (id 0x14), total data (bytes):", len(self.data))

    def check(self):
        pass


class BlockPause:
    """
    000 2  Pause time in ms
    """

    ID = 0x20

    def __init__(self, pause=3000):
        self.pause = pause

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(self.pause.to_bytes(2, "little"))
        return content

    def set(self, content):
        self.pause = int.from_bytes(content[0:2], "little")
        return content[2:]

    def dump(self):
        print("Pause (id 0x20), time (ms):", self.pause)

    def check(self):
        if self.pause < 0:
            raise FormatError("negative pause time in Pause block")


class BlockGroupStart:
    """
    00 1  Length of the Group Name
    01 x  Group name in ASCII (please keep it under 30 characters long)
    """

    ID = 0x21

    def __init__(self):
        self.name = ""

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(len(self.name[0:30]).to_bytes(1, "little"))
        if len(self.name):
            content.extend(self.name[0:30].encode("utf-8"))
        return content

    def set(self, content):
        sz = int(content[0])
        self.name = "" if sz == 0 else content[1 : sz + 1].decode("utf-8")
        return content[sz + 1 :]

    def dump(self):
        print("GroupStart (id 0x21), name:", self.name if len(self.name) else "(void)")

    def check(self):
        pass


class BlockGroupEnd:
    """
    This block has no body
    """

    ID = 0x22

    def compose(self):
        return self.ID.to_bytes(1, "little")

    def set(self, content):
        return content

    def dump(self):
        print("GroupEnd (id 0x22)")

    def check(self):
        pass


class BlockDescription:
    """
    00 1  Length of the Text
    01 x  Text in ASCII
    """

    ID = 0x30

    def __init__(self):
        self.text = ""

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        content.extend(len(self.text[0:256]).to_bytes(1, "little"))
        content.extend(self.text[0:256].encode("utf-8"))
        return content

    def set(self, content):
        sz = int(content[0])
        self.text = content[1 : sz + 1].decode("utf-8")
        return content[sz + 1 :]

    def dump(self):
        print("Description (id 0x30), text:", self.text)

    def check(self):
        pass


class BlockArchiveInfo:
    """
    00 2  Length of the block (without these two bytes)
    02 1  Number of text strings
    03 x  Text strings:
        00 1  Text Identification byte:  00 - Full Title
                                         01 - Software House / Publisher
                                         02 - Author(s)
                                         03 - Year of Publication
                                         04 - Language
                                         05 - Game/Utility Type
                                         06 - Price
                                         07 - Protection Scheme / Loader
                                         08 - Origin
                                         FF - Comment(s)
        01 1  Length of text
        02 x  Text in ASCII format
        .. .  Next Text

    Length: [00,01]+02
    """

    FULLTITLE = 0x00
    PUBLISHER = 0x01
    AUTHOR = 0x02
    YEAR = 0x03
    LANGUAJE = 0x04
    TYPE = 0x05
    PRICE = 0x06
    LOADER = 0x07
    ORIGIN = 0x08
    COMMENT = 0xFF
    ID = 0x32

    def __init__(self):
        self.strings = []

    def add_string(self, type, string):
        self.strings.append((type, string[0:256]))

    def compose(self):
        content = bytearray()
        content.extend(self.ID.to_bytes(1, "little"))
        strings = bytearray()
        strings.extend(len(self.strings).to_bytes(1, "little"))
        for s in self.strings:
            strings.extend(s[0].to_bytes(1, "little"))
            strings.extend(len(s[1]).to_bytes(1, "little"))
            strings.extend(s[1].encode("utf-8"))
        content.extend(len(strings).to_bytes(2, "little"))
        content.extend(strings)
        return content

    def set(self, content):
        # remove block size
        content = content[2:]
        strings = content[0]
        content = content[1:]
        self.strings = []
        while strings > 0:
            type = content[0]
            sz = content[1]
            text = content[2 : 2 + sz].decode("utf-8")
            self.strings.append((type, text))
            strings = strings - 1
            content = content[0 : 2 + sz]
        return content

    def dump(self):
        print("ArchiveInfo (id 0x32), strings:", len(self.strings))
        for s in self.strings:
            print("Type", hex(s[0]), "value:", s[1])

    def check(self):
        pass


TapeBlock = Union[
    BlockNormalSpeed,
    BlockTurboSpeed,
    BlockPureTone,
    BlockDifferentPulses,
    BlockPureData,
    BlockPause,
    BlockGroupStart,
    BlockGroupEnd,
    BlockDescription,
    BlockArchiveInfo,
]


class CDT:
    BLOCKS = {
        BlockNormalSpeed.ID: BlockNormalSpeed,
        BlockTurboSpeed.ID: BlockTurboSpeed,
        BlockPureTone.ID: BlockPureTone,
        BlockDifferentPulses.ID: BlockDifferentPulses,
        BlockPureData.ID: BlockPureData,
        BlockPause.ID: BlockPause,
        BlockGroupStart.ID: BlockGroupStart,
        BlockGroupEnd.ID: BlockGroupEnd,
        BlockDescription.ID: BlockDescription,
        BlockArchiveInfo.ID: BlockArchiveInfo,
    }

    def __init__(self):
        self.header = CDTHeader()
        self.blocks: List[TapeBlock] = []

    def compose(self):
        content = bytearray()
        content.extend(self.header.compose())
        for block in self.blocks:
            content.extend(block.compose())
        return content

    def add_block(self, content):
        if len(content) > 0:
            ID = content[0]
            content = content[1:]
            if ID in self.BLOCKS:
                b = self.BLOCKS[ID]()
                content = b.set(content)
                self.blocks.append(b)
                self.add_block(content)
            else:
                raise FormatError("unsupported block ID %s" % (hex(ID)))

    def set(self, content):
        content = self.header.set(content)
        self.blocks = []
        self.add_block(content)

    def format(self):
        """Empty CDT with just a puse block with its default time of 3 seconds."""
        self.__init__()
        start_block = BlockPause()
        self.blocks.append(start_block)

    def write(self, outputfile):
        content = self.compose()
        try:
            with open(outputfile, "wb") as fd:
                fd.write(content)
        except IOError:
            print("[cdt] error trying to create the file:", outputfile)

    def read(self, inputfile):
        content = bytearray()
        chunksz = 512
        try:
            with open(inputfile, "rb") as fd:
                bytes = fd.read(chunksz)
                while bytes:
                    content.extend(bytes)
                    bytes = fd.read(chunksz)
            self.set(content)
            return True
        except IOError:
            print("[cdt] could not read file:", inputfile)
        except FormatError as e:
            print("[cdt] error in input file:", e.message)
        return False

    def _add_file(self, incontent, header, speed):
        # calculate total number of data segments of 256 bytes
        segments = []
        while len(incontent) > 0:
            segment = incontent[0:256]
            segments.append(segment)
            incontent = incontent[256:]

        while len(segments) > 0:
            """ Header """
            blocksegments = segments[0:8]
            header.block_sz = 0
            for s in blocksegments:
                header.block_sz = header.block_sz + len(s)
            header.last_block = 0x00 if len(segments) > 8 else 0xFF
            hblock = BlockTurboSpeed(speed, DEF_PAUSE_HEADER)
            hblock.data = header.compose()
            self.blocks.append(hblock)

            dblock = BlockTurboSpeed(speed, DEF_PAUSE_DATA)
            data = bytearray(b"\x16")  # sync byte for data
            """ data segments up to 8 (256 * 8 = 2K) """
            for s in blocksegments:
                # Check padding, all segments must be of 256 bytes
                if len(s) < 256:
                    s.extend(0x00 for i in range(len(s), 256))
                crc = AUX_GET_CRC(s)
                data.extend(s)
                data.extend(crc.to_bytes(2, "big"))  # !!! MSB first here
            data.extend(b"\xff\xff\xff\xff")  # trail
            dblock.data = data
            self.blocks.append(dblock)
            segments = segments[8:]
            header.block_id = header.block_id + 1
            header.first_block = 0x00

        endpause = BlockPause(DEF_PAUSE_FILE)
        self.blocks.append(endpause)

    def _add_raw(self, incontent, speed):
        block = BlockTurboSpeed(speed, DEF_PAUSE_FILE)
        data = bytearray(b"\x16")  # sync byte for data
        crc = AUX_GET_CRC(incontent)
        data.extend(data)
        data.extend(incontent)
        data.extend(crc.to_bytes(2, "big"))
        data.extend(b"\xff\xff\xff\xff")
        block.data = data
        self.blocks.append(block)

    def add_file(self, incontent, header, speed):
        if header != None:
            self._add_file(incontent, header, speed)
        else:
            self._add_raw(incontent, speed)

    def add_file_with_options(
        self,
        incontent,
        header,
        baud=2000,
        tzx_method=0,
        data_method=0,
        pause_header=DEF_PAUSE_HEADER,
        pause_data=DEF_PAUSE_DATA,
        pause_file=DEF_PAUSE_FILE,
    ):
        """
        Add a file to CDT with full control over encoding parameters.

        Args:
            incontent: File content as bytearray
            header: DataHeader object (or None for headerless)
            baud: Baud rate (1000-6000)
            tzx_method: 0=Turbo(0x11), 1=PureData(0x14), 2=Standard(0x10)
            data_method: 0=Blocks, 1=Headerless, 2=Spectrum, 3=TwoBlocks2K, 4=TwoBlocks1B
            pause_header: Pause after header in ms
            pause_data: Pause after data in ms
            pause_file: Pause after file in ms
        """
        # Validate block type combinations
        if data_method in {0, 1, 3, 4} and tzx_method == 2:
            print(
                "[WARN] Standard speed only valid for spectrum method. Falling back to turbo."
            )
            tzx_method = 0
        if data_method == 2 and tzx_method != 2:
            print(
                "[WARN] Spectrum method forces standard speed. Ignoring --tzx-method."
            )

        if data_method == 0:  # Standard blocks
            self._add_file_blocks(
                incontent,
                header,
                baud,
                tzx_method,
                pause_header,
                pause_data,
                pause_file,
            )
        elif data_method == 1:  # Headerless
            self._add_file_headerless(
                incontent,
                baud,
                tzx_method,
                pause_data,
                pause_file,
            )
        elif data_method == 2:  # Spectrum
            self._add_file_spectrum(incontent, pause_data, pause_file)
        elif data_method == 3:  # Two-blocks (2K + rest)
            first_block = min(DEF_DATA_BLOCK_SZ, len(incontent))
            remaining = len(incontent) - first_block
            plan = [first_block]
            if remaining > 0:
                plan.append(remaining)
            self._add_file_blocks(
                incontent,
                header,
                baud,
                tzx_method,
                pause_header,
                pause_data,
                pause_file,
                block_plan=plan,
            )
        elif data_method == 4:  # Two-blocks (1 byte + rest)
            first_block = min(1, len(incontent))
            remaining = len(incontent) - first_block
            plan = [first_block]
            if remaining > 0:
                plan.append(remaining)
            self._add_file_blocks(
                incontent,
                header,
                baud,
                tzx_method,
                pause_header,
                pause_data,
                pause_file,
                block_plan=plan,
            )

    def _create_block_by_method(self, tzx_method, baud, pause):
        """Create a block of the specified TZX method."""
        if tzx_method == 0:  # Turbo Speed
            return BlockTurboSpeed(baud, pause)
        elif tzx_method == 1:  # Pure Data
            return BlockPureData(baud, pause)
        elif tzx_method == 2:  # Standard Speed
            return BlockNormalSpeed(pause)
        else:
            return BlockTurboSpeed(baud, pause)  # Default

    def _build_cpc_data_block(self, chunk, sync=0x16):
        """Build CPC-style data block (sync + segments + CRC + trailer)."""
        data = bytearray()
        data.append(sync)

        # Split chunk into 256-byte segments
        offset = 0
        chunk_len = len(chunk)
        while offset < chunk_len:
            segment = bytearray(chunk[offset : offset + DEF_DATA_SEGMENT_SZ])
            if len(segment) < DEF_DATA_SEGMENT_SZ:
                segment.extend(0x00 for _ in range(len(segment), DEF_DATA_SEGMENT_SZ))
            crc = AUX_GET_CRC(segment)
            data.extend(segment)
            data.extend(crc.to_bytes(2, "big"))
            offset += DEF_DATA_SEGMENT_SZ

        # If chunk is empty, still need one padded segment for CRC compatibility
        if chunk_len == 0:
            segment = bytearray(DEF_DATA_SEGMENT_SZ)
            crc = AUX_GET_CRC(segment)
            data.extend(segment)
            data.extend(crc.to_bytes(2, "big"))

        data.extend(b"\xff\xff\xff\xff")
        return data

    def _build_standard_speed_block(self, data_bytes, flag=0xFF):
        """Build ZX Spectrum style standard speed block (flag + data + checksum)."""
        block_data = bytearray()
        checksum = flag
        block_data.append(flag)
        for byte in data_bytes:
            checksum ^= byte
            block_data.append(byte)
        block_data.append(checksum & 0xFF)
        return block_data

    def _add_file_blocks(
        self,
        incontent,
        header,
        baud,
        tzx_method,
        pause_header,
        pause_data,
        pause_file,
        block_plan=None,
    ):
        """Add file using standard CPC blocks method (with headers)."""
        if header is None:
            raise FormatError("Header required for CPC block-based methods")

        total_len = len(incontent)
        offset = 0
        block_index = 0
        plan = list(block_plan) if block_plan else []

        while offset < total_len:
            if plan:
                chunk_size = plan.pop(0)
            else:
                chunk_size = min(DEF_DATA_BLOCK_SZ, total_len - offset)

            chunk_size = min(chunk_size, total_len - offset)
            if chunk_size <= 0:
                break

            chunk = bytearray(incontent[offset : offset + chunk_size])
            offset += chunk_size

            header.block_sz = len(chunk)
            header.last_block = 0xFF if offset >= total_len else 0x00
            header.first_block = 0xFF if block_index == 0 else 0x00

            # Header block
            hblock = self._create_block_by_method(tzx_method, baud, pause_header)
            hblock.data = header.compose()
            self.blocks.append(hblock)

            # Data block
            dblock = self._create_block_by_method(tzx_method, baud, pause_data)
            dblock.data = self._build_cpc_data_block(chunk)
            dblock.payload_size = len(chunk)
            self.blocks.append(dblock)

            header.block_id += 1
            block_index += 1

        self.blocks.append(BlockPause(pause_file))

    def _add_file_headerless(self, incontent, baud, tzx_method, pause_data, pause_file):
        """Add file without AMSDOS header (direct data)."""
        block = self._create_block_by_method(tzx_method, baud, pause_data)
        payload = bytearray(incontent)
        block.data = self._build_cpc_data_block(payload)
        block.payload_size = len(payload)
        self.blocks.append(block)
        self.blocks.append(BlockPause(pause_file))

    def _add_file_spectrum(self, incontent, pause_data, pause_file):
        """Add file using ZX Spectrum compatible standard speed block."""
        block = BlockNormalSpeed(pause_data)
        payload = bytearray(incontent)
        block.data = self._build_standard_speed_block(payload, flag=0xFF)
        block.payload_size = len(payload)
        self.blocks.append(block)
        self.blocks.append(BlockPause(pause_file))

    def check(self):
        self.header.check()
        for b in self.blocks:
            b.check()

    def dump(self):
        self.header.dump()
        print("")
        print(len(self.blocks), "BLOCKS:")
        for b in self.blocks:
            b.dump()


def run_read_input_file(inputfile):
    content = bytearray()
    chunksz = 65536  # 64K
    try:
        with open(inputfile, "rb") as fd:
            bytes = fd.read(chunksz)
            while bytes:
                content.extend(bytes)
                bytes = fd.read(chunksz)
        return content
    except IOError:
        print("[cdt] error reading file:", inputfile)
        sys.exit(1)


def run_new(args, cdt):
    print("[cdt] creating", args.cdtfile)
    cdt.format()
    cdt.write(args.cdtfile)
    pass


def run_check(args, cdt):
    content = run_read_input_file(args.cdtfile)
    try:
        cdt.set(content)
        cdt.check()
    except FormatError as e:
        print("[cdt] unsupported CDT format:", str(e))
        sys.exit(1)


def run_cat(args, cdt):
    run_check(args, cdt)
    cdt.dump()


def run_read_mapfile(mapfile):
    print("[cdt] reading map file", mapfile)
    try:
        with open(mapfile, "r") as fd:
            content = str.join("", fd.readlines())
            return eval(content)
    except IOError:
        print("[cdt] error reading file:", mapfile)
        sys.exit(1)


def run_get_start(startaddr, mapfile):
    try:
        addr = aux_int(startaddr)
        return addr
    except:
        startaddr = startaddr.upper()
        if startaddr in mapfile:
            return mapfile[startaddr][0]
        print("[cdt] invalid start address value")
        sys.exit(1)


def run_put_file(filein, args, cdt, header):
    run_check(args, cdt)
    content = run_read_input_file(filein)
    if len(content) > 65536:
        print("[cdt] max input file size is 64K")
        sys.exit(1)
    if header != None:
        mapfile = {}
        header.filename = "UNNAMED"
        header.addr_start = 0x4000
        header.addr_load = 0x4000
        if args.name != None:
            header.filename = args.name[0:16]
        if args.map_file != None:
            mapfile = run_read_mapfile(args.map_file)
        if args.start_addr != None:
            header.addr_start = run_get_start(args.start_addr, mapfile)
        if args.load_addr != None:
            header.addr_load = args.load_addr
    cdt.add_file(content, header, 2000 if args.speed == 1 else 1000)
    cdt.write(args.cdtfile)


def run_put_asciifile(args, cdt):
    header = DataHeader()
    header.type = DataHeader.FT_ASCII
    print("[cdt] adding ASCII file", args.put_ascii)
    run_put_file(args.put_ascii, args, cdt, header)


def run_put_binfile(args, cdt):
    header = DataHeader()
    if ".BAS" in args.put_bin.upper():
        header.type = DataHeader.FT_BAS
    else:
        header.type = DataHeader.FT_BIN
    print("[cdt] adding BIN file", args.put_bin)
    run_put_file(args.put_bin, args, cdt, header)


def run_put_rawfile(args, cdt):
    print("[cdt] adding raw file", args.put_raw)
    run_put_file(args.put_raw, args, cdt, None)


def aux_int(param):
    """
    By default, int params are converted assuming base 10.
    To allow hex values we need to 'auto' detect the base.
    """
    return int(param, 0)


# ============================================================================
# NEW COMMAND-BASED INTERFACE
# ============================================================================


def cmd_new(args):
    """Command: new - Create a new empty CDT file."""
    cdt = CDT()
    cdt.format()
    cdt.write(args.cdt_file)
    print(f"[ia2cdt] Created: {args.cdt_file}")
    return 0


def cmd_cat(args):
    """Command: cat - List CDT contents."""
    cdt = CDT()
    if not cdt.read(args.cdt_file):
        return 1

    formatter = OutputFormatter(args.format)
    output = formatter.format_cat(args.cdt_file, cdt)
    print(output)
    return 0


def cmd_check(args):
    """Command: check - Verify CDT integrity."""
    cdt = CDT()
    errors = []

    try:
        content = run_read_input_file(args.cdt_file)
        cdt.set(content)
        cdt.check()
        success = True
    except FormatError as e:
        success = False
        errors.append(str(e))
    except Exception as e:
        success = False
        errors.append(f"Unexpected error: {str(e)}")

    formatter = OutputFormatter(args.format if hasattr(args, "format") else "markdown")
    output = formatter.format_check(
        args.cdt_file, success, errors if not success else None
    )
    print(output)

    return 0 if success else 1


def cmd_save(args):
    """Command: save - Add a file to existing CDT."""
    # Read existing CDT
    cdt = CDT()
    if not cdt.read(args.cdt_file):
        print(f"[ERROR] Could not read {args.cdt_file}. Use 'new' command first.")
        return 1

    # Read input file
    try:
        content = run_read_input_file(args.file)
    except SystemExit:
        return 1

    if len(content) > 65536:
        print("[ERROR] Max input file size is 64K")
        return 1

    # Validate baud range
    baud = args.baud
    if baud < 1000 or baud > 6000:
        print("[WARN] Baud rate must be between 1000 and 6000. Clamping to range.")
        baud = max(1000, min(6000, baud))

    # Auto-detect file type if not specified
    file_type = args.type
    if not file_type:
        filename_upper = args.file.upper()
        if filename_upper.endswith(".BAS"):
            file_type = "bas"
        elif filename_upper.endswith((".TXT", ".ASC")):
            file_type = "ascii"
        else:
            file_type = "bin"

    # Create header when required (CPC block-based methods)
    header = None
    if args.data_method in {0, 3, 4}:
        header = DataHeader()
        if file_type == "bas":
            header.type = DataHeader.FT_BAS
        elif file_type == "ascii":
            header.type = DataHeader.FT_ASCII
        else:
            header.type = DataHeader.FT_BIN

        # Set name
        if args.name:
            header.filename = args.name[0:16]
        else:
            basename = os.path.basename(args.file)
            header.filename = basename[0:16]

        # Set addresses
        header.addr_load = args.load_addr if args.load_addr is not None else 0x4000
        header.addr_start = aux_int(args.start_addr) if args.start_addr else 0x4000
        header.length = len(content)

    # Add file to CDT with advanced options
    cdt.add_file_with_options(
        incontent=content,
        header=header,
        baud=baud,
        tzx_method=args.tzx_method,
        data_method=args.data_method,
        pause_header=args.pause_header,
        pause_data=args.pause_data,
        pause_file=args.pause_file,
    )

    # Write CDT
    cdt.write(args.cdt_file)
    print(f"[ia2cdt] Added {len(content)} bytes to {args.cdt_file}")
    return 0


def process_args():
    """Parse command-line arguments with subcommands."""
    parser = argparse.ArgumentParser(
        prog="ia2cdt.py",
        description="Create and manage Amstrad CPC tape images (.cdt files)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"ia2cdt {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: new
    parser_new = subparsers.add_parser("new", help="Create a new empty CDT file")
    parser_new.add_argument("cdt_file", help="CDT file to create")

    # Command: cat
    parser_cat = subparsers.add_parser("cat", help="List CDT contents")
    parser_cat.add_argument("cdt_file", help="CDT file to read")
    parser_cat.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # Command: check
    parser_check = subparsers.add_parser("check", help="Verify CDT format integrity")
    parser_check.add_argument("cdt_file", help="CDT file to check")
    parser_check.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # Command: save
    parser_save = subparsers.add_parser("save", help="Add a file to existing CDT")
    parser_save.add_argument("cdt_file", help="CDT file to modify")
    parser_save.add_argument("--file", required=True, help="File to add")
    parser_save.add_argument(
        "--name", help="Name displayed when loading (max 16 chars)"
    )
    parser_save.add_argument(
        "--type",
        choices=["bin", "bas", "ascii"],
        help="File type (default: auto-detect from extension)",
    )
    parser_save.add_argument(
        "--baud", type=int, default=2000, help="Baud rate 1000-6000 (default: 2000)"
    )
    parser_save.add_argument(
        "--load-addr", type=aux_int, help="Load address (hex or decimal)"
    )
    parser_save.add_argument(
        "--start-addr", type=str, help="Execution/call address (hex or decimal)"
    )
    parser_save.add_argument(
        "--tzx-method",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="TZX method: 0=Turbo(0x11), 1=PureData(0x14), 2=Standard(0x10)",
    )
    parser_save.add_argument(
        "--data-method",
        type=int,
        choices=[0, 1, 2, 3, 4],
        default=0,
        help="Data encoding: 0=Blocks, 1=Headerless, 2=Spectrum, 3=TwoBlocks2K, 4=TwoBlocks1B",
    )
    parser_save.add_argument(
        "--pause-header",
        type=int,
        default=DEF_PAUSE_HEADER,
        help=f"Pause after header in ms (default: {DEF_PAUSE_HEADER})",
    )
    parser_save.add_argument(
        "--pause-data",
        type=int,
        default=DEF_PAUSE_DATA,
        help=f"Pause after data in ms (default: {DEF_PAUSE_DATA})",
    )
    parser_save.add_argument(
        "--pause-file",
        type=int,
        default=DEF_PAUSE_FILE,
        help=f"Pause after file in ms (default: {DEF_PAUSE_FILE})",
    )

    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    """Main entry point with subcommand dispatch."""
    args = process_args()

    # Dispatch to command handler
    commands = {"new": cmd_new, "cat": cmd_cat, "check": cmd_check, "save": cmd_save}

    if args.command in commands:
        exit_code = commands[args.command](args)
        sys.exit(exit_code)
    else:
        print(f"[ERROR] Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
