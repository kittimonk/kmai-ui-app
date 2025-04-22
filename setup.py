
from setuptools import setup, find_packages
import os
from pathlib import Path

# The directory containing this file
HERE = Path(__file__).parent

def read_requirements(filename):
    requirements = []
    try:
        with open(filename) as f:
            reqs = f.read().splitlines()
            for req in reqs:
                if req.strip() and not req.startswith('#'):
                    requirements.append(req)
    except FileNotFoundError:
        print(f"Warning: {filename} not found!")
    return requirements

# Read requirements
requires = read_requirements('requirements.txt')
tests_requires = read_requirements('test-requirements.txt')
requires.extend(tests_requires)

# This call to setup() does all the work
setup(
    name="kmai-ent03-ui-app",
    version="1.0.6",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=requires,
    cmdclass={
        "test": lambda: None,  # Placeholder that won't actually run tests during setup.py test
    },
    entry_points={
        "console_scripts": [
            "kmai-ent03-ui-app=kmai_ent03_ui_app.app:app",
        ],
    },
)
