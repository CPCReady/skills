# CPCReady Skills — Project Guidelines

## Project Overview

This repo packages **two AI agent skills** for Amstrad CPC retro computing development, distributed via the [Agent Skills standard](https://agentskills.io). Skills are consumed with:

```bash
npx skills add CPCReady/skills
```

Compatible platforms: OpenCode, Claude Code, GitHub Copilot, Cursor, Windsurf, Cline.

## Skills

| Skill | Tool | Purpose | Entry point |
|-------|------|---------|-------------|
| `cdt` | `ia2cdt.py` | Create/manage CDT/TZX tape images | [SKILL.md](../skills/cdt/SKILL.md) |
| `dsk` | `iaDSK` (binary) | Create/manage DSK disk images | [SKILL.md](../skills/dsk/SKILL.md) |

## Architecture

```
plugin.json          ← Skill package manifest (name, version, skills path)
skills/
  cdt/               ← Self-contained: SKILL.md + agents/ + scripts/ + references/
  dsk/               ← Self-contained: SKILL.md + agents/ + scripts/ + assets/bin/
```

Each skill is **fully self-contained**. Do not introduce shared modules or cross-skill dependencies.

## Conventions

### Documentation — multi-language required
Every skill and the root must have three doc files:
- `README.md` — language-neutral (or primary)
- `README.en.md` — English
- `README.es.md` — Spanish

`SKILL.md` is written in **Spanish** (primary agent instruction language for this project).

### Output format — Markdown-first
Both tools default to **Markdown** output for human readability. JSON is opt-in via `--format json` (shell) or `-Format json` (PowerShell). Do not change the default to plain text.

Agent instructions must: **hide raw command execution** and present the result as rendered Markdown.

### CDT skill (`ia2cdt.py`)
- Pure Python 3.6+, **zero external dependencies** (stdlib only). Keep it that way.
- CLI reference: [skills/cdt/references/cli-recipes.md](../skills/cdt/references/cli-recipes.md)

### DSK skill (iaDSK)
- Pre-compiled binaries committed to `assets/bin/<platform>/` — no build system.
- Platform matrix: `linux-x64`, `linux-arm64`, `macos-x64`, `macos-arm64`, `windows-x64`.
- Install/run via wrapper scripts (`install_iadsk.sh/.ps1`, `run_iadsk.sh/.ps1`).
- CLI reference: [skills/dsk/references/cli-recipes.md](../skills/dsk/references/cli-recipes.md)
- When adding a new iaDSK binary version, replace all platform binaries in sync.

### Packaging — Agent Skills spec
- `plugin.json` is the manifest; keep `skills` path pointing to `./skills/`.
- Each skill dir must contain a `SKILL.md` as the main agent instruction file.
- Agent configs live in `agents/openai.yaml` within each skill.

## Key File Paths

| What | Where |
|------|-------|
| Skill manifest | [plugin.json](../plugin.json) |
| CDT skill instructions | [skills/cdt/SKILL.md](../skills/cdt/SKILL.md) |
| CDT tape tool | [skills/cdt/scripts/ia2cdt.py](../skills/cdt/scripts/ia2cdt.py) |
| CDT CLI reference | [skills/cdt/references/cli-recipes.md](../skills/cdt/references/cli-recipes.md) |
| DSK skill instructions | [skills/dsk/SKILL.md](../skills/dsk/SKILL.md) |
| DSK run wrapper (Unix) | [skills/dsk/scripts/run_iadsk.sh](../skills/dsk/scripts/run_iadsk.sh) |
| DSK install (Unix) | [skills/dsk/scripts/install_iadsk.sh](../skills/dsk/scripts/install_iadsk.sh) |
| DSK CLI reference | [skills/dsk/references/cli-recipes.md](../skills/dsk/references/cli-recipes.md) |
