# Security Notice

## Binary Files

This skills package includes pre-compiled binaries for the iaDSK tool:

### Location
`skills/dsk/assets/bin/<platform>/iaDSK`

### Platforms
- linux-x64 (ELF 64-bit executable)
- linux-arm64 (ELF 64-bit executable)
- macos-x64 (Mach-O 64-bit executable)
- macos-arm64 (Mach-O 64-bit executable)
- windows-x64 (PE32+ executable)

### Source and Verification

**Tool**: iaDSK - Amstrad CPC Disk Image Editor  
**Original Author**: Sid/Impact (Emmanuel Messulam)  
**License**: GPL v3  
**Source Repository**: https://github.com/mdystiq/iaDSK

#### Binary Checksums

You can verify the binaries with these SHA256 checksums:

```bash
# Generate checksums
cd skills/dsk/assets/bin
find . -type f -exec shasum -a 256 {} \;
```

**Current checksums** (as of commit ee41b16):
```
7533dcb6b7f85bfedeec858a023b4fcb6e36f06195eaa1092b5024760381d16c  windows-x64/iaDSK.exe
42e10c234358de8a9f61926230e0cf4f2cf25be8a0f21dd47cdf8540f7bde60d  linux-arm64/iaDSK
42e10c234358de8a9f61926230e0cf4f2cf25be8a0f21dd47cdf8540f7bde60d  linux-x64/iaDSK
46752031f954ed695d098c5becd016186a75d1ec40ac5afc566d300faa22e0d1  macos-arm64/iaDSK
d7c4b8f856bc622587b6e7acfca4578e6f44929fd8f0f135e7a6e6e01366cdae  macos-x64/iaDSK
```

**Note**: linux-x64 and linux-arm64 have identical checksums, which may indicate the same binary was used for both.

### Why Pre-compiled Binaries?

These binaries are included for convenience to provide a zero-configuration experience:
- No compilation toolchain required
- Cross-platform support out of the box
- Consistent behavior across environments

### Build From Source (Alternative)

If you prefer to compile from source:

```bash
# Clone the original repository
git clone https://github.com/mystiq/iaDSK.git
cd iaDSK

# Compile (requires gcc/clang)
make

# Use your own binary
./skills/dsk/scripts/run_iadsk.sh --binary /path/to/your/iaDSK -- help
```

## Python Scripts

### ia2cdt.py

**Location**: `skills/cdt/scripts/ia2cdt.py`  
**Language**: Python 3.6+  
**Dependencies**: Standard library only (no external packages)  
**License**: GPL v3

This script creates and manages CDT/TZX tape image files for Amstrad CPC. It:
- Reads and writes binary files
- Executes with standard Python interpreter
- No network access
- No system modifications beyond writing output files

**Audit**: The full source code is available in the repository and can be reviewed before use.

## Permissions Required

### File System
- **Read**: Configuration files, input files (.bin, .bas, .dsk, .cdt)
- **Write**: Output files (.dsk, .cdt) in user-specified locations
- **Execute**: iaDSK binaries, Python interpreter

### Network
- **None** - No network access required or used

### System
- **None** - No system-level modifications

## Reporting Security Issues

If you discover a security vulnerability, please email:
- **Contact**: contact@cpcready.com
- **GitHub**: https://github.com/CPCReady/skills/security

## Transparency

All source code and binaries are:
- ✅ Version controlled in public repository
- ✅ GPL v3 / MIT licensed
- ✅ Available for inspection
- ✅ Documented with checksums (planned)

---

*Last updated: March 2026*
