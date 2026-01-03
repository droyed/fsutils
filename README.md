# fsutils

[![PyPI Version](https://img.shields.io/pypi/v/fsutils.svg)](https://pypi.org/project/fsutils/)
[![Python Versions](https://img.shields.io/pypi/pyversions/fsutils.svg)](https://pypi.org/project/fsutils/)
[![License](https://img.shields.io/pypi/l/fsutils.svg)](https://opensource.org/licenses/MIT/)

A Python package providing `DirManager` class for directory/file operations and `io` module for standalone file I/O.

## Features

- **Directory Management**: Create, list, and delete directories with `DirManager`
- **Optimized Scanning**: `scan()` method with Schwartzian Transform for efficient metadata retrieval
- **File Operations**: Copy, move, and delete files within a directory context
- **Pattern Matching**: Find files using glob patterns
- **Directory Traversal**: Walk through directory trees with `Path` objects
- **Extension Filtering**: List files by type (images, videos, audio, documents)
- **Statistics**: Display directory statistics with file breakdown
- **Standalone I/O**: Simple file read/write operations with `io` module
- **Directory Utilities**: Simple directory functions with `dirs` module
- **Type Hints**: Full type annotation support

## Installation

```bash
pip install fsutils
```

### With Development Dependencies

```bash
pip install fsutils[dev]
```

### Development Installation (Editable)

For contributing or modifying the source code, install in editable mode:

```bash
pip install -e .
```

### Install from GitHub

Install the latest version directly from GitHub:

```bash
pip install git+https://github.com/droyed/fsutils.git
```

---

## Quick Start

```python
from fsutils import DirManager, io, dirs

# Directory operations with DirManager
dm = DirManager("/path/to/project")

# Create directories
dm.create_dir("data/output")

# Simple directory utilities with dirs module
dirs.mkdir("temp")
dirs.mkdirs(["cache", "logs", "backups"])

# List all Python files
py_files = dm.list_files(extensions=['.py'])
print(f"Found {len(py_files)} Python files")

# Find files with glob pattern
configs = dm.glob("**/*.json")

# Walk directory tree
for dirpath, dirs, files in dm.walk():
    print(f"Directory: {dirpath}")

# Simple file I/O with io module
data = io.read_json("config.json")
io.write_json("output.json", data)
```

---

## Basic Operations

### DirManager: Directory Operations

```python
from fsutils import DirManager

dm = DirManager("/path/to/project")

# Create directory (nested)
dm.create_dir("src/utils")

# List directory contents
contents = dm.list_dir()

# List files recursively
all_files = dm.list_files()

# List image files only
images = dm.list_images()

# Delete directory
dm.delete_dir("temp", recursive=True)
```

### DirManager: File Operations

```python
# Copy file
dm.copy_file("data.txt", "backup/data.txt")

# Move file
dm.move_file("old.txt", "archive/old.txt")
```

### io Module: File I/O

```python
from fsutils import io

# Read/Write Text
text = io.read_text("file.txt")
io.write_text("output.txt", "content")

# Read/Write JSON
data = io.read_json("config.json")
io.write_json("output.json", {"key": "value"})

# Check existence
if io.exists("file.txt"):
    print("File exists!")

# Get file info
size = io.get_file_size("file.txt")
hash = io.get_file_hash("file.txt")
```

---

## io Module

For simple file operations that don't require a base directory:

| Function | Description |
|----------|-------------|
| `io.read_text()` / `io.write_text()` | Read/write text files |
| `io.read_bytes()` / `io.write_bytes()` | Read/write binary files |
| `io.read_json()` / `io.write_json()` | Read/write JSON files |
| `io.read_pickle()` / `io.write_pickle()` | Read/write pickle files |
| `io.exists()` / `io.is_file()` / `io.is_dir()` | Path checks |
| `io.delete_file()` | Delete a file |
| `io.get_file_size()` / `io.get_modified_time()` / `io.get_file_hash()` | Metadata |

Extension constants available: `IMAGE_EXTENSIONS`, `VIDEO_EXTENSIONS`, `AUDIO_EXTENSIONS`, `DOCUMENT_EXTENSIONS`

---

## Documentation

For complete documentation, see:

- **[docs/USAGE_DirManager.md](docs/USAGE_DirManager.md)** - Comprehensive `DirManager` usage guide
- **[docs/USAGE_io.md](docs/USAGE_io.md)** - Comprehensive `io` module documentation
- **[docs/USAGE_dirs.md](docs/USAGE_dirs.md)** - Comprehensive `dirs` module documentation
- **[src/fsutils/io.py](src/fsutils/io.py)** - `io` module source code

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full changelog.
