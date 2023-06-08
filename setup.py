import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyadapt",
    version=os.environ["CIRCLE_TAG"],
    url="https://github.com/syngenta-digital/package-python-adapt.git",
    author="Demetrius Bankhead, DevOps Engineer, Syngenta Digital",
    author_email="demetrius.bankhead@syngenta.com",
    description="Syngenta's open source ADAPT-based implementation in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.0",
    install_requires=[],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
