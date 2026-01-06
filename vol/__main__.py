"""Entry point for python -m vol and PyInstaller binary"""

import sys
import os

# Add the vol package to path when running as PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
    from vol.cli import main
else:
    # Running as module
    from .cli import main

if __name__ == "__main__":
    main()
