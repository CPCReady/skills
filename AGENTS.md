# AGENTS.md — Developer Guide for AI Coding Agents

This guide provides coding conventions, commands, and patterns for agents working in the CPCReady Skills repository.

## Project Overview

**Type:** AI Agent Skills Package for Amstrad CPC retro computing  
**Distribution:** `npx skills add CPCReady/skills`  
**License:** MIT  
**Repository:** https://github.com/CPCReady/skills

### Skills Included
- **cdt** — Python tool for CDT/TZX tape image management (`ia2cdt.py`)
- **dsk** — Multi-platform binaries for DSK disk image management (`iaDSK`)

### Agent Installation

**Important:** Skills and agents are separate in OpenCode:

1. **Skills** → Installed via `npx skills add CPCReady/skills`
   - Installed to: `~/.agents/skills/`
   - Contains: Tools, scripts, documentation
   - Automatic installation

2. **Agents** → Installed manually via `./install-agent.sh`
   - Installed to: `~/.config/opencode/agents/amstrad.md`
   - Contains: AI instructions, behavior rules
   - Manual installation required (OpenCode only)

**Why separate?**
- Skills are portable across AI assistants (OpenCode, Claude Code, Cursor, etc.)
- Agents are OpenCode-specific configuration
- Users can use skills without agents (direct command execution)
- Agent provides enhanced UX (interactive prompts, safety checks)

## Output Format Philosophy

**BREAKING CHANGE:** All CPCReady skills now emit **JSON by default**. Markdown is still available, but only when explicitly requested.

- **Default output**: JSON (no `--format` flag needed)
- **Markdown override**: `--format markdown` (shell) / `-Format markdown` (PowerShell)
- **Agent responsibility**: Parse JSON → Format Markdown → Present to user (never show raw JSON/commands)

### DSK Catalog Formatting Rules

JSON structure (`cat` command):
```json
{
  "dsk": "demo.dsk",
  "entries": [
    {
      "name": "PROGRAM.BIN",
      "user": 0,
      "load": 16384,
      "exec": 16384,
      "size_kb": 2,
      "read_only": true,
      "system": false
    }
  ],
  "used_kb": 2,
  "total_kb": 178
}
```

Render as Markdown table with columns `Name | User | Size | Load | Exec | Attr`. Convert `load`/`exec` to hex (`0x4000`). Translate attributes: `read_only → R`, `system → S`, `RS` if both.

### CDT Catalog Formatting Rules

JSON structure (`cat` command): array of blocks
```json
[
  {
    "index": 1,
    "type": "Turbo Speed",
    "data_bytes": 263,
    "pause_ms": 15,
    "header": {
      "filename": "program.bin",
      "type": "BIN",
      "load_addr": "0x4000",
      "start_addr": "0x4000",
      "length": 325
    }
  }
]
```

Render as Markdown table with `# | Type | Size | Pause | Filename | File Type | Load | Exec | Length`. Use header values directly (already hex strings).

### Presentation Rules

1. Execute command silently (JSON default)
2. Parse JSON structure
3. Format Markdown table + summary line (if applicable)
4. Present formatted Markdown only; hide commands and raw JSON

This philosophy ensures agents always operate on structured data, then render user-friendly output on demand.

## Build, Test, and Lint Commands

### Current Status
⚠️ **No automated build/test/lint infrastructure currently exists.**

The project uses:
- Direct Python script execution (no build step)
- Pre-compiled binaries (committed to repo)
- Manual testing and code review

### Running Tools Manually

**CDT (Python):**
```bash
# Direct execution
python3 skills/cdt/scripts/ia2cdt.py new test.cdt
python3 skills/cdt/scripts/ia2cdt.py save test.cdt --file loader.bin
python3 skills/cdt/scripts/ia2cdt.py cat test.cdt
```

**DSK (Shell/PowerShell wrappers):**
```bash
# Unix/Linux/macOS
./skills/dsk/scripts/run_iadsk.sh -- help
./skills/dsk/scripts/run_iadsk.sh -- cat --dsk demo.dsk

# Windows
.\skills\dsk\scripts\run_iadsk.ps1 -- help
.\skills\dsk\scripts\run_iadsk.ps1 -- cat --dsk demo.dsk
```

### Future Testing (Not Yet Implemented)
If you add tests, consider:
- `pytest` for Python (ia2cdt.py)
- `bats` or `shunit2` for shell scripts
- Platform-specific CI matrix for binary wrappers

## Code Style Guidelines

### Python (ia2cdt.py)

**General Rules:**
- **Python 3.6+ stdlib only** — ZERO external dependencies (non-negotiable)
- **4-space indentation**
- **Type hints encouraged** but not mandatory
- **f-strings** for string formatting

**Naming Conventions:**
```python
# Constants
AMSDOS_BAS_TYPE = 0
DEF_DATA_BLOCK_SZ = 2048

# Classes
class OutputFormatter:
    """PascalCase with docstrings."""
    pass

# Functions
def run_read_input_file(inputfile):
    """snake_case with verb prefixes."""
    pass

# Private methods
def _format_cat_markdown(self, blocks):
    """Leading underscore for internal use."""
    pass
```

**Imports:**
```python
# Standard library only, alphabetical
import argparse
import json
import math
import os
import sys
from typing import List, Union
```

**Error Handling:**
```python
# Exit with clear error messages
if not os.path.exists(cdt_file):
    print(f"ERROR: CDT file '{cdt_file}' not found", file=sys.stderr)
    sys.exit(1)
```

**Documentation:**
- Module-level docstring with GPL v3 header (ia2cdt.py uses GPL)
- Class docstrings describing purpose
- Complex function docstrings for non-obvious logic

### Shell Scripts (Bash)

**Header:**
```bash
#!/usr/bin/env bash
set -euo pipefail  # Strict error handling always
```

**Naming:**
```bash
# Variables: lowercase_with_underscores
binary=""
output_format="markdown"

# Functions: snake_case
resolve_platform() {
    local uname_s uname_m  # Local vars declared
    # ...
}
```

**Best Practices:**
- Always quote variables: `"$variable"`
- Use arrays for argument lists: `args=()`
- Prefer `[[ ]]` over `[ ]` for conditionals

### PowerShell

**Header:**
```powershell
[CmdletBinding(PositionalBinding = $false)]
Param(
    [string]$Binary,
    [ValidateSet("markdown", "json")]
    [string]$Format = "markdown"
)
$ErrorActionPreference = "Stop"
```

**Naming:**
```powershell
# Variables: PascalCase
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Functions: Verb-Noun (PowerShell convention)
function Resolve-IadskBinary {
    param([string]$ExplicitPath)
}
```

## Documentation Standards

### Multi-Language Requirement
Every skill and the root **must** have three README files:
- `README.md` — Language-neutral quick start or selector
- `README.en.md` — Full English documentation
- `README.es.md` — Full Spanish documentation

### SKILL.md Format
- Written in **Spanish** (primary agent instruction language)
- YAML frontmatter with `name:` and `description:`
- Sections: Flujo recomendado, Comandos, Recursos, Troubleshooting
- Special section: "Presenting results to the user" (for agent UX)

**Example SKILL.md structure:**
```markdown
---
name: cdt
description: Crear y gestionar imágenes .cdt...
---

# cdt

## Flujo recomendado
## Comandos disponibles
## Recursos
## Troubleshooting
```

### CLI Reference Files
Located in `skills/*/references/cli-recipes.md`:
- Complete command syntax
- All flags and options documented
- Common usage recipes
- Error codes and troubleshooting

## Architecture Principles

### Self-Contained Skills
Each skill is **fully self-contained** with no shared dependencies:
```
skills/cdt/
  ├── SKILL.md           # Agent instructions
  ├── agents/
  │   └── openai.yaml    # Agent-specific config
  ├── scripts/
  │   └── ia2cdt.py      # Tool implementation
  ├── references/
  │   └── cli-recipes.md # CLI reference
  └── examples/          # Sample files
```

**Do NOT:**
- Create shared utility modules between skills
- Add cross-skill dependencies
- Modify one skill while working on another

### Output Format Philosophy (Agent UX)

Reinforcing the JSON-first model:
- Tools emit JSON unless `--format markdown`/`-Format markdown` is explicitly set
- Agents parse JSON, convert to Markdown tables, and show users the formatted result
- Never expose raw commands, binary paths, or JSON payloads

**Presentation Checklist:**
1. Execute command silently (JSON default)
2. Parse JSON in-memory
3. Render Markdown tables + summaries (no code blocks)
4. Present all entries; avoid truncation or omission

## Binary Management (DSK Skill)

### Platform Matrix
Pre-compiled binaries committed to `assets/bin/<platform>/`:
- `linux-x64`
- `linux-arm64`
- `macos-x64`
- `macos-arm64`
- `windows-x64`

### Updating Binaries
When adding a new iaDSK version:
1. **Update ALL platform binaries in sync** (not just one)
2. Test install/run scripts on each platform
3. Update version references in documentation

## Git Workflow

### Commit Messages
Follow conventional style:
```
Add cdt skill for Amstrad CPC tape image management
Update README with CDT examples
Fix: ia2cdt.py checksum validation for headerless blocks
```

### Before Committing
Manual checks (no pre-commit hooks configured):
- [ ] Python scripts run without errors
- [ ] Shell scripts pass `shellcheck` (if available)
- [ ] All three README files updated (root + skill-specific)
- [ ] SKILL.md updated if command syntax changed
- [ ] Both .sh and .ps1 scripts updated together

## Key File Paths

| What | Where |
|------|-------|
| Skill manifest | `plugin.json` |
| Marketplace config | `.claude-plugin/marketplace.json` |
| CDT instructions | `skills/cdt/SKILL.md` |
| CDT tool | `skills/cdt/scripts/ia2cdt.py` |
| CDT CLI ref | `skills/cdt/references/cli-recipes.md` |
| DSK instructions | `skills/dsk/SKILL.md` |
| DSK wrapper (Unix) | `skills/dsk/scripts/run_iadsk.sh` |
| DSK wrapper (Win) | `skills/dsk/scripts/run_iadsk.ps1` |
| DSK binaries | `skills/dsk/assets/bin/<platform>/` |

## Common Tasks

### Adding a New Skill
1. Create `skills/<name>/` directory
2. Add `SKILL.md` (Spanish)
3. Add three README files (root selector, .en, .es)
4. Create subdirs: `agents/`, `scripts/`, `references/`
5. Add agent config: `agents/openai.yaml`
6. Update `plugin.json` manifest
7. Update `.claude-plugin/marketplace.json` with `./skills/<name>`

### Modifying Python Tool (ia2cdt.py)
1. Edit `skills/cdt/scripts/ia2cdt.py`
2. Test manually with sample .cdt files
3. Update `skills/cdt/references/cli-recipes.md` if syntax changes
4. Update `skills/cdt/SKILL.md` if new commands added
5. Sync changes to all three README files

### Modifying Shell Wrappers (run_iadsk)
1. Edit both `.sh` and `.ps1` versions
2. Maintain feature parity between Unix and Windows
3. Test on both platforms if possible
4. Update CLI reference if flags change

### Working with Interactive Wrappers
The DSK wrappers include interactive prompt functionality for the `save` command:

**Key Principles:**
- **Never assume default values** for binary file addresses (`--load`, `--exec`)
- Let wrappers prompt users interactively for missing parameters
- Only provide addresses if user explicitly specifies them
- Non-interactive mode (pipes/automation) should fail with clear errors

**Testing Interactive Prompts:**
```bash
# Test non-interactive failure (should ERROR)
echo "test" | ./scripts/run_iadsk.sh -- save --dsk test.dsk --file program.bin

# Test with explicit addresses (should succeed)
./scripts/run_iadsk.sh -- save --dsk test.dsk --file program.bin --load 0x4000 --exec 0x4000
```

**When Adding New Prompts:**
1. Implement in both `.sh` and `.ps1` with identical behavior
2. Check for TTY/interactive mode: `[[ -t 0 ]]` (Bash) or `[Console]::IsInputRedirected` (PowerShell)
3. Fail explicitly in non-interactive mode with helpful error message
4. Loop prompts until valid input (no silent defaults)
5. Update SKILL.md with prompt documentation
6. Add examples to cli-recipes.md

## Troubleshooting

**Python import errors:**
- Verify no external dependencies were added
- Check Python version is 3.6+

**Binary not found:**
- Check `assets/bin/<platform>/` exists
- Verify install script copied to correct location
- Test binary resolution priority (PATH → default → embedded)

**Documentation out of sync:**
- Always update all three README files together
- Keep SKILL.md and cli-recipes.md in sync

---

*This guide is for AI coding agents. For user documentation, see README.en.md or README.es.md.*
