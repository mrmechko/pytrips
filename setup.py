from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

with open("README.md", "r") as fh:
    long_description = fh.read()

def install_wn(self):
    import nltk
    nltk.download("wordnet")
    nltk.download("stopwords")

class EnsureWordnet(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        install_wn()

class EnsureWordnet(develop):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        install_wn()


if __name__ == '__main__':
    setup(
        name="pytrips",
        version="0.0.1",
        author="Rik Bose",
        author_email="rbose@cs.rochester.edu",
        description="A simple python package for accessing the trips ontology and lexicon",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/mrmechko/pytrips",
        packages=find_packages(exclude=["test"]),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        install_requires=["nltk"],
        cmdclass={
            "install": EnsureWordnet,
            "develop": EnsureWordnet
        },
    )
