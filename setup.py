#!/usr/bin/env python

from setuptools import setup, find_packages
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

# Read requirements
requires = read_requirements('requirements.txt')
tests_requires = read_requirements('test-requirements.txt')

setup(
    name="kmai-ent03-ui-app",
    version="1.0.6",
    packages=find_packages(where="."),
    python_requires=">=3.10",
    install_requires=requires,
    tests_requires=tests_requires,
    package_data={
        "kmai_ent03_ui_app": ["static/*", "static/**/*"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "kmai-ent03-ui-app=kmai_ent03_ui_app.app:app",
        ],
    },
)
