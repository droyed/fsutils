# io Module Usage Guide

A comprehensive guide to using the [`io`](src/fsutils/io.py:1) module for standalone file I/O operations.

For quick start examples, see [README.md](../README.md). For directory operations, see [USAGE_DirManager.md](USAGE_DirManager.md).

## Table of Contents

- [Quick Start](#quick-start)
- [Path Checks](#path-checks)
- [Text I/O](#text-io)
- [Binary I/O](#binary-io)
- [JSON I/O](#json-io)
- [Pickle I/O](#pickle-io)
- [File Operations](#file-operations)
- [File Metadata](#file-metadata)
- [Extension Helpers](#extension-helpers)
- [Extension Constants](#extension-constants)
- [Error Handling](#error-handling)
- [Complete Example](#complete-example)
- [See Also](#see-also)

---

## Quick Start

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

## Path Checks

### exists(path)

Check if a file or directory exists.

```python
from fsutils import io

# Check if path exists
if io.exists("file.txt"):
    print("Path exists!")
else:
    print("Path does not exist")
```

**Returns:** `True` if path exists, `False` otherwise

**Parameters:**
- `path`: Path to check (str or PathLike)

---

### is_file(path)

Check if a path is a file.

```python
from fsutils import io

if io.is_file("document.pdf"):
    print("It's a file!")
```

**Returns:** `True` if path is a file, `False` otherwise

**Raises:** Nothing (returns `False` if path doesn't exist)

---

### is_dir(path)

Check if a path is a directory.

```python
from fsutils import io

if io.is_dir("/path/to/directory"):
    print("It's a directory!")
```

**Returns:** `True` if path is a directory, `False` otherwise

**Raises:** Nothing (returns `False` if path doesn't exist)

---

## Text I/O

### read_text(path, encoding='utf-8')

Read text from a file.

```python
from fsutils import io

# Read with default encoding
content = io.read_text("file.txt")

# Read with custom encoding
content = io.read_text("file.txt", encoding="latin-1")
```

**Returns:** File contents as a string

**Parameters:**
- `path`: Path to the file
- `encoding`: Text encoding to use (default: `'utf-8'`)

**Raises:**
- `FileNotFoundError` - File does not exist
- `IsADirectoryError` - Path is a directory

---

### write_text(path, content, encoding='utf-8', create_dirs=True)

Write text to a file.

```python
from fsutils import io

# Write with default settings
chars = io.write_text("output.txt", "Hello, World!")

# Write with custom encoding
io.write_text("output.txt", "Content", encoding="utf-16")

# Write without creating parent directories
io.write_text("output.txt", "Content", create_dirs=False)
```

**Returns:** Number of characters written

**Parameters:**
- `path`: Path to the file
- `content`: Text content to write
- `encoding`: Text encoding to use (default: `'utf-8'`)
- `create_dirs`: Create parent directories if they don't exist (default: `True`)

**Raises:**
- `FileNotFoundError` - Parent directory doesn't exist and `create_dirs=False`

---

## Binary I/O

### read_bytes(path)

Read binary data from a file.

```python
from fsutils import io

# Read binary data
data = io.read_bytes("image.png")

# Read binary file
binary_data = io.read_bytes("binary_file.bin")
```

**Returns:** File contents as bytes

**Raises:**
- `FileNotFoundError` - File does not exist
- `IsADirectoryError` - Path is a directory

---

### write_bytes(path, content, create_dirs=True)

Write binary data to a file.

```python
from fsutils import io

# Write binary data
bytes_written = io.write_bytes("output.bin", b"\x00\x01\x02\x03")

# Write with directory creation
io.write_bytes("path/to/file.bin", data, create_dirs=True)
```

**Returns:** Number of bytes written

**Parameters:**
- `path`: Path to the file
- `content`: Binary content to write
- `create_dirs`: Create parent directories if they don't exist (default: `True`)

**Raises:**
- `FileNotFoundError` - Parent directory doesn't exist and `create_dirs=False`

---

## JSON I/O

### read_json(path, encoding='utf-8')

Read JSON data from a file.

```python
from fsutils import io

# Read JSON file
data = io.read_json("config.json")
print(data["key"])

# Read with custom encoding
data = io.read_json("config.json", encoding="utf-8")
```

**Returns:** Parsed JSON data (dict, list, or primitive)

**Raises:**
- `FileNotFoundError` - File does not exist
- `json.JSONDecodeError` - File contains invalid JSON

---

### write_json(path, data, encoding='utf-8', indent=2, create_dirs=True)

Write JSON data to a file.

```python
from fsutils import io

# Write with default indentation (2 spaces)
io.write_json("output.json", {"key": "value"})

# Write with custom indentation
io.write_json("output.json", data, indent=4)

# Write without indentation (compact)
io.write_json("output.json", data, indent=0)

# Write with directory creation
io.write_json("path/to/output.json", data, create_dirs=True)
```

**Returns:** Number of characters written

**Parameters:**
- `path`: Path to the JSON file
- `data`: JSON-serializable data to write
- `encoding`: Text encoding to use (default: `'utf-8'`)
- `indent`: Number of spaces for indentation (default: `2`, use `0` for no indentation)
- `create_dirs`: Create parent directories if they don't exist (default: `True`)

---

## Pickle I/O

### read_pickle(path)

Read a Python object from a pickle file.

```python
from fsutils import io

# Read pickle file
obj = io.read_pickle("data.pkl")
print(type(obj))
```

**Returns:** Unpickled Python object

**Raises:**
- `FileNotFoundError` - File does not exist
- `pickle.UnpicklingError` - File contains invalid pickle data

---

### write_pickle(path, data, create_dirs=True)

Write a Python object to a pickle file.

```python
from fsutils import io

# Write pickle file
some_object = {"list": [1, 2, 3], "nested": {"key": "value"}}
bytes_written = io.write_pickle("data.pkl", some_object)

# Write with directory creation
io.write_pickle("path/to/data.pkl", some_object, create_dirs=True)
```

**Returns:** Number of bytes written

**Parameters:**
- `path`: Path to the pickle file
- `data`: Python object to pickle
- `create_dirs`: Create parent directories if they don't exist (default: `True`)

---

## File Operations

### delete_file(path)

Delete a file.

```python
from fsutils import io

# Delete a file
io.delete_file("file.txt")

# Delete with error handling
try:
    io.delete_file("file.txt")
    print("File deleted successfully")
except FileNotFoundError:
    print("File not found")
except IsADirectoryError:
    print("Path is a directory, not a file")
```

**Raises:**
- `FileNotFoundError` - File does not exist
- `IsADirectoryError` - Path is a directory

---

## File Metadata

### get_file_size(path)

Get the size of a file in bytes.

```python
from fsutils import io

# Get file size
size_bytes = io.get_file_size("file.txt")
print(f"File size: {size_bytes} bytes")

# Convert to human-readable
kb = size_bytes / 1024
mb = kb / 1024
```

**Returns:** File size in bytes

**Raises:**
- `FileNotFoundError` - File does not exist
- `IsADirectoryError` - Path is a directory

---

### get_modified_time(path)

Get the last modified time of a file or directory.

```python
from fsutils import io
from datetime import datetime

# Get modified time
mtime = io.get_modified_time("file.txt")
print(f"Modified: {mtime}")
print(f"Year: {mtime.year}")
print(f"Month: {mtime.month}")
print(f"Day: {mtime.day}")
print(f"Time: {mtime.strftime('%H:%M:%S')}")
```

**Returns:** `datetime.datetime` object

**Raises:**
- `FileNotFoundError` - Path does not exist

---

### get_file_hash(path, algorithm='md5', buffer_size=65536)

Calculate the hash of a file.

```python
from fsutils import io

# MD5 hash (default)
hash_md5 = io.get_file_hash("file.txt")
print(f"MD5: {hash_md5}")

# SHA-256 hash
hash_sha256 = io.get_file_hash("file.txt", algorithm="sha256")
print(f"SHA-256: {hash_sha256}")

# SHA-1 hash
hash_sha1 = io.get_file_hash("file.txt", algorithm="sha1")

# Custom buffer size for large files
hash_large = io.get_file_hash("large_file.iso", buffer_size=1048576)
```

**Returns:** Hexadecimal hash string

**Parameters:**
- `path`: Path to the file
- `algorithm`: Hash algorithm to use (`'md5'`, `'sha1'`, `'sha256'`, etc.)
- `buffer_size`: Size of the buffer for reading the file (default: 65536 bytes)

**Raises:**
- `FileNotFoundError` - File does not exist
- `IsADirectoryError` - Path is a directory
- `ValueError` - Algorithm is not supported

---

## Extension Helpers

### image_extensions()

Get list of common image file extensions.

```python
from fsutils import io

# Get image extensions
image_exts = io.image_extensions()
# Returns: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp']
```

**Returns:** List of image file extensions

---

### video_extensions()

Get list of common video file extensions.

```python
from fsutils import io

# Get video extensions
video_exts = io.video_extensions()
# Returns: ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v', '.mkv']
```

**Returns:** List of video file extensions

---

### audio_extensions()

Get list of common audio file extensions.

```python
from fsutils import io

# Get audio extensions
audio_exts = io.audio_extensions()
# Returns: ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.m4b', '.m4p']
```

**Returns:** List of audio file extensions

---

### document_extensions()

Get list of common document file extensions.

```python
from fsutils import io

# Get document extensions
doc_exts = io.document_extensions()
# Returns: ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']
```

**Returns:** List of document file extensions

---

## Extension Constants

Access extension lists directly without function calls:

```python
from fsutils import (
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
)

print(IMAGE_EXTENSIONS)   # ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp']
print(VIDEO_EXTENSIONS)   # ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v', '.mkv']
print(AUDIO_EXTENSIONS)   # ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.m4b', '.m4p']
print(DOCUMENT_EXTENSIONS)  # ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']

# Use with list_files() via DirManager
from fsutils import DirManager, IMAGE_EXTENSIONS

dm = DirManager("/path/to/project")
images = dm.list_files(extensions=IMAGE_EXTENSIONS)
```

---

## Error Handling

The `io` module raises standard Python exceptions:

| Exception | When Raised |
|-----------|-------------|
| `FileNotFoundError` | File or directory doesn't exist |
| `NotADirectoryError` | Path is not a directory |
| `IsADirectoryError` | Path is a directory (when file expected) |
| `json.JSONDecodeError` | Invalid JSON content |
| `pickle.UnpicklingError` | Invalid pickle data |
| `ValueError` | Unsupported hash algorithm |

### Example: Error Handling

```python
from fsutils import io

try:
    content = io.read_text("missing.txt")
except FileNotFoundError:
    print("File not found!")
except IsADirectoryError:
    print("Path is a directory!")
```

---

## Complete Example

```python
from fsutils import io, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
import os

# Read configuration
config = io.read_json("config.json")
print(f"Config: {config}")

# Write data
io.write_json("output.json", {"status": "success", "count": 42})

# Check file exists
if io.exists("data.txt"):
    size = io.get_file_size("data.txt")
    mtime = io.get_modified_time("data.txt")
    print(f"Size: {size} bytes, Modified: {mtime}")
    
    # Verify file integrity
    hash_md5 = io.get_file_hash("data.txt")
    hash_sha256 = io.get_file_hash("data.txt", algorithm="sha256")
    print(f"MD5: {hash_md5}")
    print(f"SHA-256: {hash_sha256}")

# Read and write binary
binary_data = io.read_bytes("image.png")
io.write_bytes("backup/image.png", binary_data)

# Get all media extensions
media_exts = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS
print(f"Media extensions: {media_exts}")

# Clean up
try:
    io.delete_file("temp.txt")
except FileNotFoundError:
    print("Temp file already deleted")
```

---

## See Also

- [fsutils.io Module](src/fsutils/io.py) - Source code reference
- [USAGE_DirManager.md](docs/USAGE_DirManager.md) - `DirManager` class documentation
- [README.md](README.md) - Quick getting started guide
