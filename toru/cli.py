import argparse
import sys
from .ui.app import ToruApp
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="toru",
        description="Toru - Intuitive dual-pane project & task manager for the terminal.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"toru {__version__}")
    parser.parse_args()

    app = ToruApp()
    app.run()


if __name__ == "__main__":
    main()
