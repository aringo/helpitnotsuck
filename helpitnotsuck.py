"""
This script performs linting and formatting on Python files.

It can process a single file or all Python files in a directory.
The script runs pylint, then applies formatting tools, and finally re-runs pylint.
"""

import os
import sys
from io import StringIO

import autoflake
import black
import isort
from pylint import lint
from pylint.reporters.text import TextReporter


def run_pylint(file_path: str) -> str:
    """Run pylint on a file and return the output as a string."""
    pylint_output = StringIO()
    reporter = TextReporter(pylint_output)
    lint.Run([file_path], reporter=reporter, exit=False)
    return pylint_output.getvalue()


def prompt_for_docstring(file_path: str) -> None:
    """Prompt the user for a docstring and add it to the file if missing."""
    with open(file_path, "r") as file:
        content = file.read()

    if not content.lstrip().startswith('"""'):
        print(f"No docstring found in {file_path}. Please enter a docstring:")
        docstring = input().strip()
        with open(file_path, "w") as file:
            file.write(f'"""\n{docstring}\n"""\n\n{content}')


def process_file(file_path: str) -> None:
    """Process a single Python file."""
    print(f"Processing {file_path}")

    # Run initial pylint
    print("Running initial pylint...")
    pylint_output = run_pylint(file_path)
    print(pylint_output)

    # Prompt for docstring if missing
    prompt_for_docstring(file_path)

    # Apply autoflake
    print("Applying autoflake...")
    with open(file_path, "r") as file:
        content = file.read()
    content = autoflake.fix_code(
        content, remove_all_unused_imports=True, remove_unused_variables=True
    )
    with open(file_path, "w") as file:
        file.write(content)

    # Apply isort
    print("Applying isort...")
    isort.file(file_path)

    # Apply black
    print("Applying black...")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        formatted = black.format_file_contents(
            content, fast=False, mode=black.FileMode()
        )
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(formatted)
    except black.InvalidInput:
        print(f"Warning: Black could not format {file_path}")

    # Run final pylint
    print("Running final pylint...")
    pylint_output = run_pylint(file_path)
    print(pylint_output)


def process_directory(directory: str) -> None:
    """Process all Python files in a directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))


def main():
    if len(sys.argv) != 2:
        print("Usage: python lint_and_format.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        process_file(target)
    elif os.path.isdir(target):
        process_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
