# QCmaps

Thanks for exploring this project. It was built with care for an enjoyable experience.

## Contents

- `pyproject.toml`: Example package setup file
- `qctemplate/version.py`: Example `__version__` tracking
- `.pre-commit-config.yaml`: pre-commit hook file
  - black (format code)
  - nbstripout (clear out notebook results before committing)
  - flake8 (doc-string format checking)
  - yamllint (lints yaml files)
  - yamlfmt (formats yaml files)
  - clang-format (c++ formatter)
- `.flake8`: Set to only inspect doc-strings (part of pre-commit hook)
- `.clang-format`: Formatting rules for cpp files

## Development

Please install the pre-commit hook:

```bash
pre-commit install
```

This works on a per repo basis

## Installation

Project is configured to be build with pip:

```bash
pip install .
```

With optional dependancies:

```bash
pip install ".[test]"
```

## Usage

Copy the contents of this project into your own, or use this repo as a 'template' when creating the repo

## TODO

- incorporate QCcolors
- allow clipping of geometries before plot
- add multi row plot using list of df
