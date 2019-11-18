import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rhasspy-client",
    version="1.0.0",
    author="Michael Hansen",
    author_email="hansen.mike@gmail.com",
    description="Client library for talking to remote Rhasspy server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synesthesiam/rhasspy-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
