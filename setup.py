
from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="kmai-ent03-ui-app",
    version="1.0.6",
    packages=find_packages(),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.11",
    zip_safe=False,
)
