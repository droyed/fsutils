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

    def test_scan(self, dm, temp_dir):
        """Test listing directory contents via scan."""
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()

        contents = dm.scan()
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

    def test_scan_sort_by_name(self, dm, temp_dir):
        """Test scan sorted by name (case-insensitive)."""
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "a_file.txt").write_text("content")
        (temp_dir / "m_file.txt").write_text("content")

        contents = dm.scan(sort_by='name')
        names = [p.name for p in contents]
        # Case-insensitive sorting: M comes before z, a comes first
        assert names == ['a_file.txt', 'm_file.txt', 'z_file.txt']

        contents_rev = dm.scan(sort_by='name', reverse=True)
        names_rev = [p.name for p in contents_rev]
        assert names_rev == ['z_file.txt', 'm_file.txt', 'a_file.txt']

    def test_scan_sort_by_mtime(self, dm, temp_dir):
        """Test scan sorted by modification time."""
        (temp_dir / "old_file.txt").write_text("old content")
        time.sleep(0.01)  # Ensure different mtime
        (temp_dir / "new_file.txt").write_text("new content")

        contents = dm.scan(sort_by='mtime')
        names = [p.name for p in contents]
        assert names[0] == 'old_file.txt'
        assert names[1] == 'new_file.txt'

    def test_scan_sort_by_size(self, dm, temp_dir):
        """Test scan sorted by file size."""
        (temp_dir / "small.txt").write_text("small")
        (temp_dir / "large.txt").write_text("larger content here")
        (temp_dir / "medium.txt").write_text("medium")

        contents = dm.scan(sort_by='size')
        names = [p.name for p in contents]
        assert names == ['small.txt', 'medium.txt', 'large.txt']

    def test_scan_no_sort(self, dm, temp_dir):
        """Test scan without sorting (default behavior)."""
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "a_file.txt").write_text("content")

        contents = dm.scan()  # No sort_by parameter
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

    # =======================================================================
    # Tests for relative path parameter
    # =======================================================================

    def test_scan_relative_false(self, dm, temp_dir):
        """Test scan returns absolute paths by default."""
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "subdir").mkdir()

        contents = dm.scan()
        assert all(p.is_absolute() for p in contents)
        assert contents[0].parent == temp_dir

    def test_scan_relative_true(self, dm, temp_dir):
        """Test scan returns relative paths when relative=True."""
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "subdir").mkdir()

        contents = dm.scan(relative=True)
        assert all(not p.is_absolute() for p in contents)
        names = [p.name for p in contents]
        assert "file1.txt" in names
        assert "subdir" in names

    def test_list_files_relative_false(self, dm, temp_dir):
        """Test list_files returns absolute paths by default."""
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file2.txt").write_text("content")

        files = dm.list_files()
        assert all(p.is_absolute() for p in files)
        # All files should be under temp_dir
        assert all(temp_dir in p.parents for p in files)

    def test_list_files_relative_true(self, dm, temp_dir):
        """Test list_files returns relative paths when relative=True."""
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file2.txt").write_text("content")

        files = dm.list_files(relative=True)
        assert all(not p.is_absolute() for p in files)
        names = [p.name for p in files]
        assert "file1.txt" in names
        assert "file2.txt" in names
        # Check that nested path is relative
        nested_files = [p for p in files if p.parts[0] == "dir1"]
        assert len(nested_files) == 1

    def test_list_files_relative_with_extensions(self, dm, temp_dir):
        """Test list_files with extensions and relative=True."""
        (temp_dir / "file1.py").write_text("content")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file2.py").write_text("content")
        (temp_dir / "file3.txt").write_text("content")

        files = dm.list_files(extensions=[".py"], relative=True)
        assert all(not p.is_absolute() for p in files)
        assert all(p.suffix == ".py" for p in files)
        assert len(files) == 2

    def test_list_images_relative_false(self, dm, temp_dir):
        """Test list_images returns absolute paths by default."""
        (temp_dir / "image1.jpg").write_bytes(b"\x00\x01\x02")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "image2.png").write_bytes(b"\x00\x01\x02\x03")

        images = dm.list_images()
        assert all(p.is_absolute() for p in images)

    def test_list_images_relative_true(self, dm, temp_dir):
        """Test list_images returns relative paths when relative=True."""
        (temp_dir / "image1.jpg").write_bytes(b"\x00\x01\x02")
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "image2.png").write_bytes(b"\x00\x01\x02\x03")

        images = dm.list_images(relative=True)
        assert all(not p.is_absolute() for p in images)
        names = [p.name for p in images]
        assert "image1.jpg" in names
        assert "image2.png" in names

    def test_glob_relative_false(self, dm, temp_dir):
        """Test glob returns absolute paths by default."""
        (temp_dir / "file1.py").write_text("# Python")
        (temp_dir / "file2.py").write_text("# Python")

        py_files = dm.glob("*.py")
        assert all(p.is_absolute() for p in py_files)
        assert py_files[0].parent == temp_dir

    def test_glob_relative_true(self, dm, temp_dir):
        """Test glob returns relative paths when relative=True."""
        (temp_dir / "file1.py").write_text("# Python")
        (temp_dir / "file2.py").write_text("# Python")

        py_files = dm.glob("*.py", relative=True)
        assert all(not p.is_absolute() for p in py_files)
        names = [p.name for p in py_files]
        assert "file1.py" in names
        assert "file2.py" in names

    def test_walk_relative_false(self, dm, temp_dir):
        """Test walk yields paths (dirnames/filenames relative to dirpath)."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file1.txt").write_text("content")
        (temp_dir / "dir2").mkdir()
        (temp_dir / "dir2" / "file2.txt").write_text("content")

        for dirpath, dirnames, filenames in dm.walk():
            # dirpath is absolute
            assert dirpath.is_absolute()
            # dirnames and filenames are relative to dirpath
            assert all(not d.is_absolute() for d in dirnames)
            assert all(not f.is_absolute() for f in filenames)

    def test_walk_relative_true(self, dm, temp_dir):
        """Test walk yields relative paths when relative=True."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "file1.txt").write_text("content")
        (temp_dir / "dir2").mkdir()
        (temp_dir / "dir2" / "file2.txt").write_text("content")

        for dirpath, dirnames, filenames in dm.walk(relative=True):
            assert not dirpath.is_absolute()
            assert not dirpath.parts[0] == str(temp_dir.parts[0]) if dirpath.parts else True
            assert all(not d.is_absolute() for d in dirnames)
            assert all(not f.is_absolute() for f in filenames)

    def test_walk_relative_nested_paths(self, dm, temp_dir):
        """Test walk with relative=True returns correct nested paths."""
        (temp_dir / "root_dir").mkdir()
        (temp_dir / "root_dir" / "subdir").mkdir()
        (temp_dir / "root_dir" / "subdir" / "file.txt").write_text("content")

        for dirpath, dirnames, filenames in dm.walk(relative=True):
            if filenames:
                # All paths should be relative to base_dir
                assert not dirpath.is_absolute()
                for f in filenames:
                    assert not f.is_absolute()
                    # The file path should include subdirectory name
                    if "subdir" in str(f):
                        assert f.parts[0] == "root_dir"

    # =======================================================================
    # Tests for list_subdirs method
    # =======================================================================

    def test_list_subdirs_basic(self, dm, temp_dir):
        """Test basic subdirectory listing includes base_dir."""
        # Create nested directory structure
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "dir2").mkdir()
        (temp_dir / "dir1" / "dir2" / "dir3").mkdir()
        (temp_dir / "file1.txt").write_text("content")
        
        subdirs = dm.list_subdirs()
        
        # Should include base_dir + all subdirectories
        assert len(subdirs) == 4
        # All should be directories
        assert all(p.is_dir() for p in subdirs)
        # Base dir should be in results
        assert temp_dir in subdirs
        
    def test_list_subdirs_max_depth_0(self, dm, temp_dir):
        """Test list_subdirs with max_depth=0 returns only base_dir."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "dir2").mkdir()
        
        subdirs = dm.list_subdirs(max_depth=0)
        
        # Only base_dir at depth 0
        assert len(subdirs) == 1
        assert subdirs[0] == temp_dir
        
    def test_list_subdirs_max_depth_1(self, dm, temp_dir):
        """Test list_subdirs with max_depth=1 returns base_dir + immediate children."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir2").mkdir()
        (temp_dir / "dir1" / "dir3").mkdir()
        
        subdirs = dm.list_subdirs(max_depth=1)
        
        # base_dir + 2 immediate children = 3
        assert len(subdirs) == 3
        assert temp_dir in subdirs
        
    def test_list_subdirs_max_depth_2(self, dm, temp_dir):
        """Test list_subdirs with max_depth=2 includes nested directories."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "dir2").mkdir()
        (temp_dir / "dir1" / "dir2" / "dir3").mkdir()
        
        subdirs = dm.list_subdirs(max_depth=2)
        
        # base_dir + dir1 + dir2 = 3
        assert len(subdirs) == 3
        
    def test_list_subdirs_empty_dir(self, dm, temp_dir):
        """Test list_subdirs on empty directory returns only base_dir."""
        subdirs = dm.list_subdirs()
        
        assert len(subdirs) == 1
        assert subdirs[0] == temp_dir
        
    def test_list_subdirs_sort_by_name(self, dm, temp_dir):
        """Test list_subdirs sorted by name."""
        (temp_dir / "z_dir").mkdir()
        (temp_dir / "a_dir").mkdir()
        (temp_dir / "m_dir").mkdir()
        
        subdirs = dm.list_subdirs(sort_by='name')
        names = [p.name for p in subdirs]
        
        # All 4 directories should be present (base_dir + 3 subdirs)
        assert len(names) == 4
        # Should be sorted alphabetically
        assert names == sorted(names)
        
        # Reverse sort
        subdirs_rev = dm.list_subdirs(sort_by='name', reverse=True)
        names_rev = [p.name for p in subdirs_rev]
        assert names_rev == sorted(names_rev, reverse=True)
        
    def test_list_subdirs_sort_by_mtime(self, dm, temp_dir):
        """Test list_subdirs sorted by modification time."""
        (temp_dir / "old_dir").mkdir()
        time.sleep(0.01)
        (temp_dir / "new_dir").mkdir()
        
        subdirs = dm.list_subdirs(sort_by='mtime')
        names = [p.name for p in subdirs]
        
        # All 3 directories should be present (base_dir + 2 subdirs)
        assert len(names) == 3
        # Old dir should come before new dir (by mtime)
        assert names.index('old_dir') < names.index('new_dir')
        
    def test_list_subdirs_sort_by_size(self, dm, temp_dir):
        """Test list_subdirs sorted by directory size."""
        (temp_dir / "small_dir").mkdir()
        (temp_dir / "small_dir" / "small.txt").write_text("small")
        (temp_dir / "large_dir").mkdir()
        (temp_dir / "large_dir" / "large.txt").write_text("much larger content here")
        
        subdirs = dm.list_subdirs(sort_by='size')
        names = [p.name for p in subdirs]
        
        # Base dir + small_dir + large_dir
        assert len(names) == 3
        # Large dir should have larger size than small_dir
        assert names.index('large_dir') > names.index('small_dir')
        
    def test_list_subdirs_relative_true(self, dm, temp_dir):
        """Test list_subdirs returns relative paths when relative=True."""
        (temp_dir / "dir1").mkdir()
        (temp_dir / "dir1" / "dir2").mkdir()
        
        subdirs = dm.list_subdirs(relative=True)
        
        # All paths should be relative
        assert all(not p.is_absolute() for p in subdirs)
        # Names should be correct (base_dir becomes '.', which has empty name)
        names = [p.name for p in subdirs]
        assert '' in names  # base_dir relative path is '.' which has empty name
        assert 'dir1' in names
        assert 'dir2' in names
        
    def test_list_subdirs_relative_false(self, dm, temp_dir):
        """Test list_subdirs returns absolute paths by default."""
        (temp_dir / "dir1").mkdir()
        
        subdirs = dm.list_subdirs()
        
        # All paths should be absolute
        assert all(p.is_absolute() for p in subdirs)
        # Base dir should be temp_dir
        assert subdirs[0] == temp_dir

    # =======================================================================
    # Tests for scan method (canonical directory listing)
    # =======================================================================

    def test_scan_not_a_directory(self, dm, temp_dir):
        """Test scan raises error when path is not a directory."""
        (temp_dir / "file.txt").write_text("content")

        with pytest.raises(NotADirectoryError, match="Path is not a directory"):
            dm.scan("file.txt")

    def test_scan_nonexistent(self, dm, temp_dir):
        """Test scan raises error when path does not exist."""
        with pytest.raises(NotADirectoryError, match="does not exist"):
            dm.scan("nonexistent")

    def test_scan_subdirectory(self, dm, temp_dir):
        """Test scan on a subdirectory."""
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "nested.txt").write_text("content")

        contents = dm.scan("subdir")
        names = [p.name for p in contents]
        assert "nested.txt" in names
