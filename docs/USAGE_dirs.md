# dirs Module Usage Guide

A guide to using the [`dirs`](src/fsutils/dirs.py:1) module for simple directory utility functions.

For quick start examples, see [README.md](../README.md).

---

## Functions

### mkdirs(dirns)

Create multiple directories if they don't exist.

```python
from fsutils import dirs

# Create multiple directories
dirs.mkdirs(["dir1", "dir2/nested", "dir3/deep/nested"])
```

**Parameters:**
- `dirns`: List of directory paths to create

**Note:** Each directory is created with `os.makedirs()`, which creates nested directories.

---

### mkdir(dirn)

Create a single directory if it doesn't exist.

```python
from fsutils import dirs

# Create single directory
dirs.mkdir("new_directory")

# Create nested directory
dirs.mkdir("parent/child")
```

**Parameters:**
- `dirn`: Directory path to create

---

### newmkdir(P)

Create a fresh directory by removing an existing one first.

```python
from fsutils import dirs

# Remove existing directory and create fresh one
dirs.newmkdir("cache")
```

**Warning:** This will recursively delete the entire directory if it already exists.

**Parameters:**
- `P`: Directory path to create fresh

---

## Importing

```python
# Import entire module
import fsutils.dirs as dirs
dirs.mkdir("mydir")

# Import specific functions
from fsutils.dirs import mkdir, mkdirs, newmkdir

# Import all functions
from fsutils.dirs import *
```

---

## See Also

- [USAGE_DirManager.md](USAGE_DirManager.md) - `DirManager` class for advanced directory operations
- [USAGE_io.md](USAGE_io.md) - `io` module for file I/O operations
- [src/fsutils/dirs.py](src/fsutils/dirs.py) - Source code reference
