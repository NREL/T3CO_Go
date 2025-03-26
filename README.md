# T3CO-Go

This repo contains a web-based dashboard called T3CO-Go for NREL's comprehensive total cost of ownership tool, T3CO.

## Overview

This is a template for your NREL Python Package

## Installation

Go to [Installation Guide](./docs/installation.md)

T3CO-Go can be installed from two sources: PyPI or GitHub

### Installation Source #1: PyPI

From within the [Python environment](./docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO-Go`) and run one of these three installation options:

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

From within the [Python environment](./docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO_Go`) and run this command:

```bash
pip install -e .
```

## Quick Start

Go to [Quick Start Guide](./docs/quick_start.md)

## Starting a T3CO-Go instance

After installing T3CO_Go within a Python environment using one of the two sources, run this command:

```bash
run_t3co_go
```

This will open a web browser tab with T3CO prepared to run on your local machine in the background.

## Acknowledgements

## How to Cite this tool
