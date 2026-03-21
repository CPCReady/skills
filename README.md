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
npx skills add CPCReady/skills/dsk
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
