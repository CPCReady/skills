# Security Notice

## Python Scripts

### iadsk.py

**Location**: `skills/dsk/scripts/iadsk.py`  
**Language**: Python 3.6+  
**Dependencies**: Standard library only (no external packages)  
**License**: GPL v3  
**Author**: Destroyer  
**Version**: 1.0.0

This tool manages DSK disk images for Amstrad CPC. It:
- Creates and validates DSK format
- Reads/writes files with AMSDOS headers
- Supports BASIC, binary, ASCII, and raw files
- No network access
- No system modifications beyond output files

**Audit**: Full source code available in repository and reviewable.

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

## Why Python Only?

Both tools are pure Python for:
- **Zero security alerts**: No compiled binaries to execute
- **Transparency**: Full source code visible and auditable
- **Cross-platform**: Works on Windows, macOS, Linux with Python 3
- **No dependencies**: Only uses Python standard library

## Permissions Required

### File System
- **Read**: Input files (.bin, .bas, .dsk, .cdt)
- **Write**: Output files (.dsk, .cdt) in user-specified locations

### Execute
- Python interpreter only (no external binaries)

### Network
- **None** - No network access required or used

### System
- **None** - No system-level modifications

## Reporting Security Issues

If you discover a security vulnerability, please:
- **Email**: contact@cpcready.com
- **GitHub**: https://github.com/CPCReady/skills/security

## Transparency

All source code is:
- ✅ Version controlled in public repository
- ✅ GPL v3 / MIT licensed
- ✅ Available for inspection and audit
- ✅ No compiled binaries
- ✅ Zero external dependencies

---

*Last updated: March 2026*
