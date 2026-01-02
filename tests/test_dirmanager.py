"""Test suite for DirManager class (directory operations)."""

import time
from pathlib import Path

import pytest

from fsutils import DirManager


class TestDirManager:
    """Test cases for the DirManager class."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    @pytest.fixture
    def dm(self, temp_dir):
        """Create a DirManager instance with temporary directory."""
        return DirManager(str(temp_dir))

    def test_version(self):
        """Test that version is defined."""
        from fsutils import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_init_with_current_directory(self, temp_dir):
        """Test initialization with current working directory."""
        import os

        dm = DirManager()
        expected = Path(os.getcwd()).resolve()
        assert dm.base_dir.resolve() == expected

    def test_init_with_valid_directory(self, temp_dir):
        """Test initialization with a valid directory."""
        dm = DirManager(str(temp_dir))
        assert dm.base_dir == temp_dir

    def test_init_with_invalid_directory(self, tmp_path):
        """Test initialization with non-existent directory raises ValueError."""
        with pytest.raises(ValueError, match="Base directory does not exist"):
            DirManager(str(tmp_path / "nonexistent"))

    def test_create_dir(self, dm, temp_dir):
        """Test creating a directory."""
        new_dir = dm.create_dir("new_directory")
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_dir_nested(self, dm, temp_dir):
        """Test creating nested directories."""
        new_dir = dm.create_dir("parent/child/grandchild")
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_list_dir(self, dm, temp_dir):
        """Test listing directory contents."""
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()

        contents = dm.list_dir()
        names = [p.name for p in contents]

        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir" in names

    def test_copy_file(self, dm, temp_dir):
        """Test copying a file."""
        source = temp_dir / "source.txt"
        source.write_text("source content")

        dst = dm.copy_file("source.txt", "destination.txt")

        assert dst.exists()
        assert dst.read_text() == "source content"

    def test_move_file(self, dm, temp_dir):
        """Test moving a file."""
        source = temp_dir / "source.txt"
        source.write_text("source content")

        dst = dm.move_file("source.txt", "moved.txt")

        assert dst.exists()
        assert dst.read_text() == "source content"
        assert not source.exists()

    def test_delete_dir_empty(self, dm, temp_dir):
        """Test deleting an empty directory."""
        subdir = temp_dir / "empty_dir"
        subdir.mkdir()

        dm.delete_dir("empty_dir")
        assert not subdir.exists()

    def test_delete_dir_recursive(self, dm, temp_dir):
        """Test recursively deleting a directory."""
        subdir = temp_dir / "nonempty_dir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")

        dm.delete_dir("nonempty_dir", recursive=True)
        assert not subdir.exists()

    def test_glob(self, dm, temp_dir):
        """Test glob pattern matching."""
        (temp_dir / "file1.py").write_text("# Python")
        (temp_dir / "file2.py").write_text("# Python")
        (temp_dir / "file.txt").write_text("text")

        py_files = dm.glob("*.py")
        assert len(py_files) == 2

        txt_files = dm.glob("*.txt")
        assert len(txt_files) == 1

    def test_walk(self, dm, temp_dir):
        """Test directory tree walking."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file1.txt").write_text("content")
        (temp_dir / "dir1" / "file2.txt").write_text("content")
        (temp_dir / "dir2").mkdir()
        (temp_dir / "dir2" / "file3.txt").write_text("content")

        all_files = []
        for dirpath, dirnames, filenames in dm.walk():
            all_files.extend(filenames)

        assert len(all_files) == 3

    def test_list_files(self, dm, temp_dir):
        """Test recursive file listing."""
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file2.txt").write_text("content")
        (temp_dir / "dir1" / "dir2").mkdir()
        (temp_dir / "dir1" / "dir2" / "file3.txt").write_text("content")

        files = dm.list_files()
        assert len(files) == 3

    def test_list_files_with_extensions(self, dm, temp_dir):
        """Test file listing with extension filter."""
        (temp_dir / "file1.py").write_text("content")
        (temp_dir / "file2.txt").write_text("content")
        (temp_dir / "file3.py").write_text("content")

        py_files = dm.list_files(extensions=[".py"])
        assert len(py_files) == 2
        assert all(f.suffix == ".py" for f in py_files)

    def test_list_files_with_max_depth(self, dm, temp_dir):
        """Test file listing with max depth."""
        (temp_dir / "file1.txt").write_text("content")  # depth 0
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file2.txt").write_text("content")  # depth 1
        (temp_dir / "dir1" / "dir2").mkdir()
        (temp_dir / "dir1" / "dir2" / "file3.txt").write_text("content")  # depth 2

        all_files = dm.list_files()
        assert len(all_files) == 3

        depth_1_files = dm.list_files(max_depth=1)
        assert len(depth_1_files) == 2

    def test_list_dir_sort_by_name(self, dm, temp_dir):
        """Test listing directory sorted by name."""
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "a_file.txt").write_text("content")
        (temp_dir / "m_file.txt").write_text("content")

        contents = dm.list_dir(sort_by='name')
        names = [p.name for p in contents]
        assert names == ['a_file.txt', 'm_file.txt', 'z_file.txt']

        contents_rev = dm.list_dir(sort_by='name', reverse=True)
        names_rev = [p.name for p in contents_rev]
        assert names_rev == ['z_file.txt', 'm_file.txt', 'a_file.txt']

    def test_list_dir_sort_by_mtime(self, dm, temp_dir):
        """Test listing directory sorted by modification time."""
        (temp_dir / "old_file.txt").write_text("old content")
        time.sleep(0.01)  # Ensure different mtime
        (temp_dir / "new_file.txt").write_text("new content")

        contents = dm.list_dir(sort_by='mtime')
        names = [p.name for p in contents]
        assert names[0] == 'old_file.txt'
        assert names[1] == 'new_file.txt'

    def test_list_dir_sort_by_size(self, dm, temp_dir):
        """Test listing directory sorted by file size."""
        (temp_dir / "small.txt").write_text("small")
        (temp_dir / "large.txt").write_text("larger content here")
        (temp_dir / "medium.txt").write_text("medium")

        contents = dm.list_dir(sort_by='size')
        names = [p.name for p in contents]
        assert names == ['small.txt', 'medium.txt', 'large.txt']

    def test_list_dir_no_sort(self, dm, temp_dir):
        """Test listing directory without sorting (default behavior)."""
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "a_file.txt").write_text("content")

        contents = dm.list_dir()  # No sort_by parameter
        assert len(contents) == 2

    def test_list_files_sort_by_name(self, dm, temp_dir):
        """Test recursive file listing sorted by name."""
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "a_file.txt").write_text("content")
        (temp_dir / "dir1" / "m_file.txt").write_text("content")

        files = dm.list_files(sort_by='name')
        names = [p.name for p in files]
        assert names == ['a_file.txt', 'm_file.txt', 'z_file.txt']

        files_rev = dm.list_files(sort_by='name', reverse=True)
        names_rev = [p.name for p in files_rev]
        assert names_rev == ['z_file.txt', 'm_file.txt', 'a_file.txt']

    def test_list_files_sort_by_mtime(self, dm, temp_dir):
        """Test recursive file listing sorted by modification time."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "old_file.txt").write_text("old")
        time.sleep(0.01)
        (temp_dir / "new_file.txt").write_text("new")

        files = dm.list_files(sort_by='mtime')
        names = [p.name for p in files]
        assert names == ['old_file.txt', 'new_file.txt']

    def test_list_files_sort_by_size(self, dm, temp_dir):
        """Test recursive file listing sorted by file size."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "small.txt").write_text("small")
        (temp_dir / "dir1" / "large.txt").write_text("much larger content here")

        files = dm.list_files(sort_by='size')
        names = [p.name for p in files]
        assert names == ['small.txt', 'large.txt']

    def test_list_images_sort(self, dm, temp_dir):
        """Test list_images with sorting."""
        (temp_dir / "z_image.jpg").write_bytes(b'\x00\x01\x02')
        (temp_dir / "a_image.png").write_bytes(b'\x00\x01\x02\x03')

        images = dm.list_images(sort_by='name')
        names = [p.name for p in images]
        assert names == ['a_image.png', 'z_image.jpg']

    def test_repr(self, dm, temp_dir):
        """Test __repr__ method returns unambiguous representation."""
        repr_str = repr(dm)
        assert "DirManager" in repr_str
        assert str(temp_dir) in repr_str
        assert "base_dir=" in repr_str

    def test_str(self, dm, temp_dir):
        """Test __str__ method returns user-friendly representation."""
        str_repr = str(dm)
        assert "DirManager" in str_repr
        assert str(temp_dir) in str_repr

    def test_eq_same_directory(self, temp_dir):
        """Test __eq__ returns True for DirManager with same base_dir."""
        dm1 = DirManager(str(temp_dir))
        dm2 = DirManager(str(temp_dir))
        assert dm1 == dm2

    def test_eq_different_directory(self, temp_dir):
        """Test __eq__ returns False for DirManager with different base_dir."""
        dm1 = DirManager(str(temp_dir))
        other_dir = temp_dir / "other"
        other_dir.mkdir()
        dm2 = DirManager(str(other_dir))
        assert dm1 != dm2

    def test_eq_notimplemented(self, dm):
        """Test __eq__ returns NotImplemented for non-DirManager comparison."""
        assert dm.__eq__("not a DirManager") == NotImplemented
        assert dm.__eq__(123) == NotImplemented
        assert dm.__eq__(None) == NotImplemented

    def test_hash(self, dm):
        """Test __hash__ method makes DirManager hashable."""
        # Should be able to hash the DirManager
        hash_value = hash(dm)
        assert isinstance(hash_value, int)

    def test_hash_set(self, temp_dir):
        """Test DirManager can be used in a set."""
        dm1 = DirManager(str(temp_dir))
        dm2 = DirManager(str(temp_dir))
        # Same directory should have same hash
        assert hash(dm1) == hash(dm2)
        # Should be able to add to a set
        dm_set = {dm1}
        assert dm1 in dm_set
        # Adding identical DirManager won't add duplicate
        dm_set.add(dm2)
        assert len(dm_set) == 1

    def test_hash_dict_key(self, dm):
        """Test DirManager can be used as a dictionary key."""
        dm_dict = {dm: "value"}
        assert dm_dict[dm] == "value"

    def test_display_stats(self, dm, temp_dir):
        """Test display_stats method prints directory statistics."""
        # Create some test files and directories
        (temp_dir / "file1.py").write_text("# Python file")
        (temp_dir / "file2.txt").write_text("text content")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.py").write_text("# Another Python file")

        # Capture the output
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output
        dm.display_stats()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()

        # Verify the output contains expected information
        assert "📁" in output  # Directory icon
        assert "📄" in output  # File icon
        assert "Files:" in output
        assert "Directories:" in output
        assert "Total size:" in output
        assert "Top Extensions:" in output

    def test_display_stats_follow_symlinks(self, dm, temp_dir):
        """Test display_stats with follow_symlinks parameter."""
        # Create a test file
        (temp_dir / "file.txt").write_text("content")

        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output
        dm.display_stats(follow_symlinks=True)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert "📁" in output
        assert "Files:" in output
