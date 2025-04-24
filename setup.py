#!/usr/bin/env python

from setuptools import setup, find_packages #, Command
import os
from pathlib import Path

# The directory containing this file
HERE = Path(__file__).parent

def read_requirements(filename):
    requirements = []
    try:
        with open(os.path.join(HERE, filename), 'r') as f:
            reqs = f.read().splitlines()
            for req in reqs:
                if req.strip() and not req.startswith('#'):
                    requirements.append(req)
    except FileNotFoundError:
        print(f"Warning: {filename} not found!")
    return requirements

#class PyTestCommand(Command):
#    description = "Run tests with pytest"
#    user_options = []

#    def initialize_options(self):
#        pass

#    def finalize_options(self):
#        pass

#    def run(self):
#        # Import here so that setup.py doesn't need pytest unless you actually run tests
#        import pytest

#        errno = pytest.main(["--maxfail=1", "--disable-warnings", "tests"])
#        raise SystemExit(errno)

# Read requirements
requires = read_requirements('requirements.txt')
tests_requires = read_requirements('test-requirements.txt')
#requires.extend(tests_requires)

setup(
    name="kmai-ent03-ui-app",
    version="1.0.6",
    packages=find_packages(where="."),
#    packages=find_packages(where="kmai_ent03_ui_app"), # FInd packages in the 'kmai_ent03_ui_app' directory
#    package_dir={"": "kmai_ent03_ui_app"}, # Set the base directory for packages to 'kmai_ent03_ui_app'
    python_requires=">=3.10",
    install_requires=requires,
#    tests_requires=tests_requires,
    package_data={
        "kmai_ent03_ui_app": ["static/*", "static/**/*"],
    },
    include_package_data=True,
#    cmdclass={
#        "test": PyTestCommand, # override the old 'test' command
#    },
    entry_points={
        "console_scripts": [
            "kmai-ent03-ui-app=kmai_ent03_ui_app.app:app",
        ]
#    entry_points={
#        "console_scripts": [
#            "runserver=app:app",
#        ]       
    },
)
