[![homepage](https://img.shields.io/badge/homepage-t3co_go-blue)](https://www.nrel.gov/transportation/t3co.html) [![github](https://img.shields.io/badge/github-t3co_go-blue.svg)](https://github.com/NREL/T3CO_Go) [![documentation](https://img.shields.io/badge/documentation-t3co_go-blue.svg)](https://nrel.github.io/T3CO_Go/) [![PyPI - Version](https://img.shields.io/pypi/v/t3co-go)](https://pypi.org/project/t3co-go/) ![GitHub License](https://img.shields.io/github/license/NREL/T3CO_Go) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/t3co-go)

# T3CO-Go

This repo contains a web-based dashboard called T3CO-Go for NREL's [Transportation Technology Total Cost of Ownership tool, T3CO](https://nrel.github.io/T3CO/).

## Installation

For detailed instructions for setting up enviroment and other prerequisites  to [Installation Guide](https://github.com/NREL/T3CO_Go/blob/main/docs/installation.md)

T3CO-Go can be installed from two sources: PyPI or GitHub

### Installation Source #1: PyPI

From within the [Python environment](https://github.com/NREL/T3CO_Go/blob/main/docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO-Go`) and run one of these three installation options:

For the default option/extra:

```bash
pip install t3co_go
```

### Installation Source #2: From a git clone of the repository

T3CO-Go can also be installed from a clone of the GitHub repository.

First, [clone](https://git-scm.com/docs/git-clone) the repository from [GitHub](https://github.com/NREL/T3CO_Go) from your desired directory (eg., /Users/Projects/):

```bash
git clone https://github.com/NREL/T3CO_Go.git T3CO_Go
```

This creates a git compliant folder 'T3CO_Go' (i.e., a '/Users/Projects/T3CO_Go' folder)

From within the [Python environment](https://github.com/NREL/T3CO_Go/blob/main/docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO_Go`) and run this command:

```bash
pip install -e .
```

## Quick Start

Go to [Quick Start Guide](https://github.com/NREL/T3CO_Go/blob/main/docs/quick_start.md)

## Starting a T3CO-Go instance

After installing T3CO_Go within a Python environment using one of the two sources, run this command:

```bash
run_t3co_go
```

This will open a web browser tab with T3CO prepared to run on your local machine in the background.

## Acknowledgements

## How to Cite this tool
