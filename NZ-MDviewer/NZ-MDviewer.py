#!/usr/bin/env python3
import sys
import os
# Ensure this directory is on sys.path so sibling modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deps import provjeri_dependencije
provjeri_dependencije()
from main_window import main

if __name__ == "__main__":
    main()
