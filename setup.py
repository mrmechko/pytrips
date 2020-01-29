from setuptools import setup, find_packages
from setuptools.command.install import install as _install

with open("README.md", "r") as fh:
    long_description = fh.read()

extras = {
    "tools": [
        'spacy>=2.0.0,<3.0.0',
        'en_core_web_lg==2.1.0',
        ]
    }

base = [
        "nltk",
        "jsontrips>=0.1.26",
        "graphviz"
    ]

if __name__ == '__main__':
    setup(
        name="pytrips",
        version="0.5.9",
        author="Rik Bose",
        author_email="rbose@cs.rochester.edu",
        description="A simple python package for accessing the trips ontology and lexicon",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/mrmechko/pytrips",
        packages=find_packages(exclude=["test"]),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
            "Operating System :: OS Independent",
        ],
        install_requires=base,
        extras_require=extras,
    )
