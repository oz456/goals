import argparse
import sys
from .ui.app import GoalsApp
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="goals",
        description="Goals - Super clean, minimal 2-pane goal & workspace manager for the terminal.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"goals {__version__}")
    parser.parse_args()

    app = GoalsApp()
    app.run()


if __name__ == "__main__":
    main()
