# Package
This is a Python Package for akeneo.

# Help to Create the Package
Based on:
https://packaging.python.org/en/latest/tutorials/packaging-projects/

https://github.com/denkiwakame/py-tiny-pkg

# Check other Python Akeneo
https://github.com/KaveTech/pyakeneo


# Build package

py -m build

# Publish Test package

py -m twine upload --repository testpypi dist/*

## Test Package Install

https://test.pypi.org/project/akeneo/0.0.2/