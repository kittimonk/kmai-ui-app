
from setuptools import setup, find_packages

setup(
    name="kmai-ent03-ui-app",  # Match the package name in your .tar.gz
    version="1.0.5",  # Match the version in your .tar.gz
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-jose==3.3.0",
        "requests==2.31.0",
        "python-multipart==0.0.6",
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.2",
        "azure-storage-file-datalake==12.12.0",
        "azure-storage-blob==12.18.0",
        "azure-identity==1.14.0",
        "azure-mgmt-cognitiveservices==13.5.0",
        "openai==1.10.0",
        "numpy==1.26.0",
        "httpx==0.24.1",
        "redis==5.0.1",
        "pyodbc==5.0.1",
        "striprtf==0.0.18",
        "azure-search-documents==11.4.0",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
