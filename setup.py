from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytrips",
    version="0.0.1",
    author="Rik Bose",
    author_email="rbose@cs.rochester.edu",
    description="A simple python package for accessing the trips ontology and lexicon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrmechko/pytrips",
    packages=find_namespace_packages(include=["pytrips.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
