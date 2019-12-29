import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setuptools.setup(
    name="rhasspy-client",
    version=version,
    author="Michael Hansen",
    author_email="hansen.mike@gmail.com",
    description="Client library for talking to remote Rhasspy server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synesthesiam/rhasspy-client",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
