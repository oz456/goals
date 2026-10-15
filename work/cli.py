import argparse
import sys
from .ui.app import WorkApp
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="work",
        description="Work - Intuitive dual-pane project & task manager for the terminal.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"work {__version__}")
    parser.parse_args()

    app = WorkApp()
    app.run()


if __name__ == "__main__":
    main()
