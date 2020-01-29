set -e
echo "releasing a new ${1:-patch}"
bumpversion ${1:-patch}
rm -rf build 
rm -rf dist
python setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
