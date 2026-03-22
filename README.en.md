# Amstrad CPC Skills

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/CPCReady/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Amstrad CPC](https://img.shields.io/badge/Amstrad-CPC-orange)](https://www.cpcwiki.eu/)
[![Skills](https://img.shields.io/badge/skills.sh-available-purple)](https://skills.sh)

> Professional skills for Amstrad CPC retro computing development

---

## Installation

Install all skills:

```bash
npx skills add CPCReady/skills
```

Install a specific skill:

```bash
npx skills add CPCReady/skills/dsk   # Disk images
npx skills add CPCReady/skills/cdt   # Tape images
```

---

## Available Skills

### 🖥️ dsk - iaDSK Disk Image Editor

Automation for iaDSK, a command-line tool to create, edit, and manage Amstrad CPC `.dsk` disk images.

#### Features
- Cross-platform support (Windows, macOS, Linux)
- Embedded precompiled binaries
- Human-readable Markdown output
- JSON mode for automation
- x64 and ARM64 architecture support

#### Use Cases
- Creating or editing .dsk disk images
- Managing files on Amstrad CPC disks
- Extracting or injecting files into disk images
- Working with retro computing projects

#### Available Commands

| Command | Description |
|---------|-------------|
| `help` | Show help |
| `new` | Create new .dsk disk |
| `cat` | List disk files |
| `free` | Show free space |
| `save` | Save file to disk |
| `get` | Extract file from disk |
| `era` | Delete file from disk |
| `list` | Show content as list |
| `basic` | Show BASIC file |
| `ascii` | Show ASCII file |
| `hex` | Show content in hexadecimal |
| `disasm` | Disassemble Z80 code |
| `dams` | Assemble with DAMS |

#### File Types Supported

| Type | Code | Use |
|------|------|-----|
| ASCII | `A` | Text, documents |
| Binary | `B` | Executables, data |
| Raw | `R` | Raw data |

#### Example Prompts

```
"Create a new disk called game.dsk and add the file loader.bin to it"
"List all files on the disk retro.dsk"
"Extract all files from backup.dsk to the extraction folder"
"Show the BASIC content of the MAIN.BAS file"
"Disassemble the SPRITE.BIN file"
```

---

## Detailed Examples

### 📋 Basic Operations

#### Show help
```
"Show me the iaDSK help"
"What commands are available in iaDSK?"
```

#### Create a new disk
```
"Create a new disk called project.dsk"
"Make a new DSK image named backup.dsk"
```

#### List disk contents (catalog)
```
"Show me what's on the disk game.dsk"
"List all files on retro.dsk"
"What files are in the disk collection.dsk?"
```

#### Check free space
```
"How much free space is on demo.dsk?"
"Check the available space on backup.dsk"
```

---

### 💾 File Operations

#### Save ASCII text files
```
"Add the file readme.txt to disk docs.dsk as ASCII"
"Save intro.txt to game.dsk as a text file"
"Import the text file credits.txt into project.dsk"
```

#### Save binary files (executables)
```
"Add loader.bin to game.dsk as binary with load address 0x8000 and execution at 0x8000"
"Save sprite.bin to graphics.dsk as binary, load at 40000, exec at 40000"
"Import main.bin into project.dsk as binary with load and exec both at 32768"
```

#### Save raw data files
```
"Add tileset.dat to graphics.dsk as raw data"
"Save music.raw to audio.dsk as raw type"
```

#### Save with custom AMSDOS name
```
"Save loader.bin to game.dsk as binary with the name BOOT.BIN, load 0x4000, exec 0x4000"
"Add main.bas to project.dsk as ASCII with the name START.BAS"
```

#### Extract files from disk
```
"Extract program.bas from game.dsk to ./extracted/"
"Get all files from backup.dsk and save them to the output folder"
"Export loader.bin from retro.dsk to ./binaries/loader.bin"
```

#### Delete files from disk
```
"Delete the file old.bas from project.dsk"
"Remove temp.bin from game.dsk"
"Erase the file unused.dat from backup.dsk"
```

---

### 🔍 View File Contents

#### View file as raw list
```
"List the content of program.bas from game.dsk"
"Show me the raw content of data.bin on project.dsk"
```

#### View BASIC programs
```
"Show me the BASIC program main.bas from game.dsk"
"Display loader.bas from retro.dsk as BASIC with split lines"
"View the BASIC content of menu.bas on project.dsk, split by lines"
```

#### View ASCII text files
```
"Show the ASCII content of readme.txt from docs.dsk"
"Display intro.txt from game.dsk as text"
```

#### View files in hexadecimal
```
"Show sprite.bin from graphics.dsk in hexadecimal"
"Display the hex dump of loader.bin on game.dsk"
"View data.bin from backup.dsk in hex format"
```

#### Disassemble Z80 binary files
```
"Disassemble loader.bin from game.dsk"
"Show the Z80 assembly of sprite.bin on graphics.dsk"
"Disassemble main.bin from retro.dsk and show me the code"
```

#### View DAMS assembly source
```
"Show the DAMS source of sprite.asm from project.dsk"
"Display routines.dam from game.dsk as DAMS assembly"
```

---

### 📼 cdt - ia2cdt Tape Image Toolkit

Automation layer for the new Python ia2cdt script. Create and validate Amstrad CPC cassette images (`.cdt`/`.tzx`) with subcommands, advanced encoding methods, and Markdown/JSON reporting.

#### Features
- Pure Python (no native binaries) – runs on Windows, macOS, Linux.
- Subcommand CLI: `new`, `save`, `cat`, `check`.
- Data methods: standard blocks, headerless, ZX Spectrum, and two custom split strategies.
- Baud rate control (1000–6000) plus custom pauses.
- Markdown + JSON output for catalog listings and automation pipelines.

#### Use Cases
- Build multi-stage tape loaders (fast BASIC + binary payloads).
- Inject raw assets (screen dumps, music) without AMSDOS headers.
- Export structured metadata for retro tooling or CI validation.
- Validate third-party `.cdt` releases before distribution.

#### Command Summary

| Command | Description |
|---------|-------------|
| `new <cdt>` | Create a blank tape with initial pause |
| `save <cdt> --file <path>` | Append a file with configurable encoding |
| `cat <cdt> [--format json]` | List every block (Markdown or JSON) |
| `check <cdt>` | Validate structure, headers, and CRCs |

#### Data Methods

| Method | Name | Notes |
|--------|------|-------|
| `0` | Blocks | CPC AMSDOS headers + payload (default) |
| `1` | Headerless | Raw CPC block with CRC (direct RAM) |
| `2` | Spectrum | ZX/Spectrum standard-speed format |
| `3` | Two blocks 2K | First block 2048 bytes, rest of file after |
| `4` | Two blocks 1B | First block 1 byte, rest of file after |

#### Example Prompts
```
"Create a new tape named loader.cdt and add loader.bas at 6000 baud"
"Append main.bin to build.cdt at load=0x4000 exec=0x4000"
"Add screen.scr to demo.cdt headerless at 0xC000"
"Show the catalog of retro.cdt in JSON format"
"Verify the integrity of competition.cdt"
```

---

### 🎯 Complex Workflows

#### Create disk and add multiple files
```
"Create a new disk game.dsk, then add loader.bin as binary (load 0x8000, exec 0x8000), 
add main.bas as ASCII, and add sprites.bin as binary (load 0x4000, exec 0x4000)"
```

#### Backup workflow
```
"Show me all files on original.dsk, then extract all of them to ./backup/, 
then create a new disk copy.dsk and add all the extracted files"
```

#### Inspect and modify
```
"Show the contents of project.dsk, check the free space, 
then delete old.bas and temp.bin, and add new.bas as ASCII"
```

#### Development workflow
```
"Create dev.dsk, add loader.bin (binary, load 0x8000, exec 0x8000), 
add game.bas (ASCII), add sprites.bin (binary, load 0xC000), 
then show me the final catalog and free space"
```

#### Binary analysis
```
"Extract loader.bin from game.dsk, show me its hex dump, 
then disassemble it to see the Z80 assembly code"
```

---

### 🔧 Advanced Options

#### Use custom AMSDOS filename (8.3 format)
```
"Save my_long_filename.bin to game.dsk as LOADER.BIN with load 0x8000 and exec 0x8000"
```

#### Specify user number (0-15)
```
"Save config.dat to disk.dsk as ASCII with user number 5"
"Add hidden.bin to secret.dsk as binary (load 0x4000, exec 0x4000) with user 7"
```

#### Set read-only protection
```
"Save important.bas to backup.dsk as ASCII and mark it as read-only"
"Add system.bin to boot.dsk as binary (load 0x4000, exec 0x4000) with read-only protection"
```

#### Set system file attribute
```
"Save kernel.bin to os.dsk as binary (load 0x0000, exec 0x0000) and mark it as a system file"
```

---

### 📦 Batch Operations

#### Process multiple disks
```
"Show me the catalog for disk1.dsk, disk2.dsk, and disk3.dsk"
"Check the free space on all disks: game1.dsk, game2.dsk, game3.dsk"
```

#### Organize by file type
```
"Extract all .BAS files from project.dsk to ./basic/, 
all .BIN files to ./binaries/, and all .TXT files to ./text/"
```

---

### 🚨 Error Handling Examples

#### When disk doesn't exist
```
User: "Show contents of missing.dsk"
Agent: Will show error message indicating the disk file was not found
```

#### When file doesn't exist on disk
```
User: "Extract nonexistent.bas from game.dsk"
Agent: Will show error indicating the file is not on the disk
```

#### When file already exists on disk
```
User: "Add loader.bin to game.dsk"
Agent: If LOADER.BIN already exists, will show error. 
       User can then delete the old file first or use a different name.
```

---

### 💡 Tips

- **File naming**: AMSDOS uses 8.3 format (8 chars name, 3 chars extension). Long filenames are automatically truncated.
- **Addresses**: Can be specified in decimal (32768) or hexadecimal (0x8000 or 8000h)
- **User numbers**: Range 0-15, default is 0. User 0 is standard, others can organize files.
- **Protection**: Read-only and system attributes help protect important files.
- **Disk capacity**: Standard CPC disks hold 178 KB (Data format) or 169 KB (System format)
- **File types**: ASCII for text/BASIC, Binary for executables, Raw for pure data

---

## Usage

### With OpenCode/Claude Code

Simply mention the skill in your request:

```
"Use the dsk skill to show me what's on this disk image"
```

The agent will automatically:
1. Verify if iaDSK is available
2. Install iaDSK if needed (using platform-specific scripts)
3. Execute your requested operation
4. Return results in readable format

### Platform-Specific Installation

The dsk skill includes automated installation scripts:

**macOS / Linux:**
```bash
./skills/dsk/scripts/install_iadsk.sh
```

**Windows:**
```powershell
.\skills\dsk\scripts\install_iadsk.ps1
```

### Output Formats

- **Markdown** (default): Human-readable output for interactive use
- **JSON**: Add `--format json` for programmatic parsing

---

## Repository Structure

```
CPCReady/skills/
├── .claude-plugin/          # Marketplace configuration
│   └── marketplace.json
├── skills/                  # Individual skills
│   └── dsk/                # iaDSK disk editor
│       ├── SKILL.md        # Skill instructions for agents
│       ├── agents/         # Helper agents
│       ├── assets/         # Precompiled iaDSK binaries
│       ├── references/     # iaDSK documentation
│       └── scripts/        # Installation & execution scripts
├── .gitignore
├── LICENSE                 # MIT License
├── README.md              # This file
└── plugin.json            # Plugin metadata
```

---

## Supported Platforms

These skills work with:

- [OpenCode](https://opencode.ai/)
- [Claude Code](https://claude.com/product/claude-code)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cursor](https://cursor.sh)
- [Windsurf](https://codeium.com/windsurf)
- [Cline](https://cline.bot/)
- Any other agent that supports the [Agent Skills standard](https://agentskills.io)

---

## About Amstrad CPC

The Amstrad CPC was a home personal computer released in 1984, very popular in Europe. It uses 3-inch floppy disks and has a vast library of classic software. These skills help modern developers work with CPC disk images and development tools.

---

## Troubleshooting

### Error: "iaDSK not found"

The skill includes embedded binaries. The installation script should run automatically, but you can manually trigger it:

```bash
# macOS/Linux
./skills/dsk/scripts/install_iadsk.sh

# Windows
.\skills\dsk\scripts\install_iadsk.ps1
```

### Error: "Permission denied"

Make the scripts executable:

```bash
chmod +x skills/dsk/scripts/install_iadsk.sh
chmod +x skills/dsk/scripts/run_iadsk.sh
```

### Verify Installation

```bash
./skills/dsk/scripts/run_iadsk.sh -- help
```

Should display help without errors.

---

## Resources

- **iaDSK Repository**: https://github.com/ABCronosMods/iaDSK
- **iaDSK Documentation**: https://github.com/ABCronosMods/iaDSK/tree/main/doc
- **Amstrad CPC Wiki**: https://www.cpcwiki.eu/

---

## Contributing

Contributions are welcome! If you'd like to add a new skill or improve an existing one:

1. Fork this repository
2. Create a new skill directory under `skills/`
3. Add your `SKILL.md` with proper YAML frontmatter
4. Update `.claude-plugin/marketplace.json` to include your skill
5. Test locally before submitting
6. Submit a pull request

See [Agent Skills specification](https://agentskills.io) for skill creation guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Part of the [CPCReady](https://github.com/CPCReady) organization*
