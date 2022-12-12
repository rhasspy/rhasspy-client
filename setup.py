"""Setup script for rhasspy-client package"""
import setuptools

with open("README.md", "rt", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "rt", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

with open("VERSION", "rt", encoding="utf-8") as fh:
    version = fh.read().strip()

setuptools.setup(
    name="rhasspy-client",
    version=version,
    author="Michael Hansen",
    author_email="hansen.mike@gmail.com",
    description="Client library for talking to remote Rhasspy server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rhasspy/rhasspy-client",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
