# DirManager Usage Guide

A comprehensive guide to using the [`DirManager`](src/fsutils/paths.py:28) class for directory and file operations.

For quick start examples, see [README.md](README.md).

## Table of Contents

- [Quick Start](#quick-start)
- [Initialization](#initialization)
- [Dunder Methods](#dunder-methods)
- [Directory Operations](#directory-operations)
- [File Operations](#file-operations)
- [Path Pattern Matching](#path-pattern-matching)
- [Directory Statistics](#directory-statistics)
- [Path Resolution](#path-resolution)
- [Error Handling](#error-handling)
- [Complete Example](#complete-example)
- [See Also](#see-also)

---

## Quick Start

```python
from fsutils import DirManager, io

# Initialize DirManager with a base directory
dm = DirManager("/path/to/project")

# Relative paths are resolved relative to the base directory
dm.create_dir("data")
io.write_text("data/input.txt", "content")

# List all Python files
py_files = dm.list_files(extensions=['.py'])

# Walk directory tree
for dirpath, dirs, files in dm.walk():
    print(f"Directory: {dirpath}")
    for f in files:
        print(f"  File: {f}")
```

---

## Initialization

The `DirManager` can be initialized in multiple ways:

```python
from fsutils import DirManager

# With a specific directory path
dm = DirManager("/project/path")

# With no arguments (uses current working directory)
dm = DirManager()

# Raises ValueError if the directory doesn't exist
try:
    dm = DirManager("/nonexistent/path")
except ValueError as e:
    print(e)  # "Base directory does not exist: /nonexistent/path"
```

### Attributes

- `base_dir`: The pathlib.Path object for the base directory

---

## Dunder Methods

The `DirManager` class implements several dunder (double underscore) methods for improved usability and integration with Python's built-in functions.

### __repr__()

Returns an unambiguous string representation of the DirManager instance.

```python
dm = DirManager("/project/path")
print(repr(dm))
# Output: DirManager(base_dir=PosixPath('/project/path'))
```

**Returns:** Unambiguous string representation showing the class and base_dir

---

### __str__()

Returns a user-friendly string representation of the DirManager instance.

```python
dm = DirManager("/project/path")
print(str(dm))
# Output: DirManager(/project/path)
```

**Returns:** Human-readable string showing the class and base directory

---

### __eq__(other)

Compares two DirManager instances for equality based on their `base_dir`.

```python
dm1 = DirManager("/project/path")
dm2 = DirManager("/project/path")
dm3 = DirManager("/other/path")

print(dm1 == dm2)  # True - same base_dir
print(dm1 == dm3)  # False - different base_dir
print(dm1 == "not a DirManager")  # NotImplemented
```

**Returns:** `True` if other is a DirManager with the same base_dir, `False` otherwise

---

### __hash__()

Returns a hash value for the DirManager instance, making it hashable and usable in sets and as dictionary keys.

```python
dm = DirManager("/project/path")

# Use as dictionary key
dm_dict = {dm: "value"}
print(dm_dict[dm])  # Output: value

# Use in sets
dm_set = {dm}
print(dm in dm_set)  # Output: True

# Hash equality for same directory
dm2 = DirManager("/project/path")
print(hash(dm) == hash(dm2))  # True
```

**Returns:** Integer hash value based on the base_dir path

---

## Directory Operations

### create_dir(path, exist_ok=True)

Create a single directory or nested directories.

```python
# Create single directory
dm.create_dir("output")

# Create nested directories
dm.create_dir("a/b/c")

# Won't raise error if exists
dm.create_dir("existing", exist_ok=True)
```

**Returns:** `pathlib.Path` object for the created directory

**Raises:** `FileExistsError` if directory exists and `exist_ok=False`

---

### list_dir(path='.', sort_by=None, reverse=False)

List contents of a directory.

```python
# List base directory
contents = dm.list_dir()

# List subdirectory
contents = dm.list_dir("subfolder")

# Sort alphabetically
contents = dm.list_dir(sort_by='name')

# Sort by modification time (newest first)
contents = dm.list_dir(sort_by='mtime', reverse=True)

# Sort by size
contents = dm.list_dir(sort_by='size')
```

**sort_by options:**
- `'name'` - Sort alphabetically
- `'mtime'` - Sort by modification time
- `'size'` - Sort by file size
- `None` - No sorting (default)

**Returns:** List of `pathlib.Path` objects

**Raises:**
- `FileNotFoundError` if directory doesn't exist
- `NotADirectoryError` if path is not a directory

---

### list_files(max_depth=None, extensions=None, sort_by=None, reverse=False)

List all files recursively, optionally filtered by extension.

```python
# All files in project
all_files = dm.list_files()

# Only 2 levels deep
files = dm.list_files(max_depth=2)

# Specific file types
py_files = dm.list_files(extensions=['.py', '.txt'])

# Sort by name
files = dm.list_files(sort_by='name')

# Sort by size (largest first)
files = dm.list_files(sort_by='size', reverse=True)
```

**Parameters:**
- `max_depth`: Maximum recursion depth (None for unlimited)
- `extensions`: List of extensions to filter (e.g., `['.py', '.txt']`)
- `sort_by`: Sort criteria ('name', 'mtime', 'size', or None)
- `reverse`: Reverse the sort order

**Returns:** List of `pathlib.Path` objects for matching files

---

### list_images(max_depth=None, sort_by=None, reverse=False)

Convenience method to list all image files recursively.

```python
# All images
images = dm.list_images()

# Top-level only
images = dm.list_images(max_depth=1)

# Sorted by name
images = dm.list_images(sort_by='name')
```

**Filters for:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.ico`, `.webp`

**Returns:** List of `pathlib.Path` objects for image files

---

### delete_dir(path, recursive=False)

Delete a directory.

```python
# Delete empty directory
dm.delete_dir("temp")

# Delete with all contents
dm.delete_dir("temp", recursive=True)
```

**Raises:**
- `FileNotFoundError` if directory doesn't exist
- `NotADirectoryError` if path is not a directory
- `OSError` if directory is not empty and `recursive=False`

---

## File Operations

### copy_file(src, dst, create_dirs=True)

Copy a file from source to destination.

```python
# Simple copy
dm.copy_file("data.txt", "backup/data.txt")

# Copy with automatic directory creation
dm.copy_file("old.txt", "new/dir/structure/new.txt")
```

**Returns:** `pathlib.Path` to the destination file

**Raises:**
- `FileNotFoundError` if source doesn't exist
- `IsADirectoryError` if source is a directory

---

### move_file(src, dst, create_dirs=True)

Move (rename) a file.

```python
# Rename file
dm.move_file("old.txt", "new.txt")

# Move and rename
dm.move_file("data.txt", "archive/data.txt")
```

**Returns:** `pathlib.Path` to the destination file

**Raises:**
- `FileNotFoundError` if source doesn't exist
- `IsADirectoryError` if source is a directory

---

## Path Pattern Matching

### glob(pattern)

Find files matching a glob pattern.

```python
# All Python files
py_files = dm.glob("*.py")

# All .txt files recursively
txt_files = dm.glob("**/*.txt")

# Python files in src/ directory
src_py = dm.glob("src/**/*.py")

# All JSON files in any subdirectory
json_files = dm.glob("**/*.json")
```

**Returns:** List of matching `pathlib.Path` objects

---

### walk(top='.')

Walk a directory tree (similar to os.walk, but returns Path objects).

```python
# Walk from base directory
for dirpath, dirs, files in dm.walk():
    print(f"\n{dirpath}:")
    for d in dirs:
        print(f"  [DIR]  {d.name}")
    for f in files:
        print(f"  [FILE] {f.name}")

# Walk from specific subdirectory
for dirpath, dirs, files in dm.walk("src"):
    print(f"Directory: {dirpath}")
```

**Yields:** Tuples of `(dirpath, dirnames, filenames)` where all are `pathlib.Path` objects

**Raises:**
- `FileNotFoundError` if top directory doesn't exist
- `NotADirectoryError` if top path is not a directory

---

## Directory Statistics

### display_stats(*, follow_symlinks=False)

Display statistics about the base directory in a formatted, colorful output.

```python
# Display statistics for the base directory
dm.display_stats()

# Follow symbolic links when scanning
dm.display_stats(follow_symlinks=True)
```

**Sample Output:**
```
📁 /path/to/project
  📄 Files:        42
  📁 Directories:  15 (hidden: 2)
  🔗 Symlinks:     3
  💾 Total size:   1.2 MB
  📦 Largest file: data.csv (256 KB)
  📊 Top Extensions:
    📦 By size   : 📄 .csv   512 KB   🐍 .py    256 KB   📝 .md    128 KB
    🔢 By count  : 🐍 .py    25      📄 .csv   10      📝 .md    5
  🆕 Recent files: 30 (last 30 days)
  📭 Empty dirs:   2
  ⚠️  Errors:       0
```

**Parameters:**
- `follow_symlinks`: If True, follow symbolic links when scanning (default: False)

**Displays:**
- File, directory, and symlink counts
- Total size and largest file
- Top extensions by size and count
- Recent files (modified in last 30 days)
- Empty directories count
- Error count

---

## Path Resolution

### _resolve_path(path)

Internal method that resolves paths relative to `base_dir`.

```python
# Absolute paths are used as-is
path = dm._resolve_path("/absolute/path")
# Result: /absolute/path

# Relative paths are joined with base_dir
path = dm._resolve_path("data/file.txt")
# Result: /project/data/file.txt
```

**Returns:** Resolved `pathlib.Path` object

---

## Error Handling

The `DirManager` class raises appropriate exceptions:

| Exception | When Raised |
|-----------|-------------|
| `FileNotFoundError` | Path doesn't exist |
| `NotADirectoryError` | Path is a file, not a directory |
| `IsADirectoryError` | Path is a directory, not a file |
| `FileExistsError` | Directory exists (when `exist_ok=False`) |
| `OSError` | Directory not empty (when `recursive=False`) |
| `ValueError` | Invalid base directory or hash algorithm |

```python
try:
    dm.list_dir("nonexistent")
except FileNotFoundError:
    print("Directory doesn't exist!")

try:
    dm.delete_dir("nonempty", recursive=False)
except OSError:
    print("Directory is not empty!")
```

---

## Complete Example

```python
from fsutils import DirManager, io
import pathlib

# Initialize with project directory
dm = DirManager("/my/project")

# Create directory structure
dm.create_dir("src")
dm.create_dir("tests")
dm.create_dir("data")
dm.create_dir("docs")

# Write files (using io module)
io.write_text("README.md", "# My Project")
io.write_json("config.json", {"debug": True, "port": 8080})

# Copy file
dm.copy_file("README.md", "docs/backup_readme.md")

# List all Python files in project
py_files = dm.list_files(extensions=['.py'])
print(f"Found {len(py_files)} Python files")

# List all images
images = dm.list_images()
print(f"Found {len(images)} image files")

# Walk directory tree and print structure
print("\nProject structure:")
for dirpath, dirs, files in dm.walk():
    level = dirpath.relative_to(dm.base_dir).parts
    indent = "  " * len(level)
    print(f"{indent}{dirpath.name}/")
    subindent = "  " * (len(level) + 1)
    for f in files:
        print(f"{subindent}{f.name}")

# Find config files
configs = dm.glob("**/*.json")
print(f"\nFound {len(configs)} JSON files")

# Move a file
dm.move_file("docs/backup_readme.md", "archive/readme_backup.md")

# Clean up temporary directory
dm.delete_dir("temp", recursive=True)
```

---

## See Also

- [USAGE_io.md](docs/USAGE_io.md) - Comprehensive `io` module documentation
- [fsutils.io Module](src/fsutils/io.py) - Source code reference
- [README.md](README.md) - Quick getting started guide
