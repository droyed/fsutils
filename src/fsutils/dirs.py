import os
import shutil


def mkdirs(dirns):
    """Create multiple directories if they don't exist."""
    for dirn in dirns:
        if not os.path.exists(dirn):
            os.makedirs(dirn)

def mkdir(dirn):
    """Create a single directory if it doesn't exist."""
    if not os.path.exists(dirn):
        os.makedirs(dirn)

def newmkdir(P):
    """Create a fresh directory by removing existing one first."""
    if os.path.isdir(P):
        shutil.rmtree(P)    
    mkdir(P)
    