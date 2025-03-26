# Installation

## Setting Up a Python Environment <a name="setting-up-env"></a>

This package depends on [Python](https://www.python.org/downloads/)>=3.8 and <=3.10. To create an environment containing the appropriate Python version and a built-in `pip`, there are two preferred ways:

1. First option is to use [**conda**](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html):

    ```bash
    conda create -n t3co_go python=3.10
    conda activate t3co_go
    ```

2. The other option is using [venv](https://docs.python.org/3/library/venv.html)

    ```bash
    python3.10 -m venv t3co_go
    ```

    On macOS/Linux, activate the environment:

    ```bash
    source t3co_go/bin/activate
    ```

    On Windows Powershell:

    ```bash
    t3co_go\Scripts\activate
    ```

## Installing T3CO-Go Python Package

T3CO-Go can be installed from two sources: PyPI or GitHub

### Installation Source #1: PyPI

From within the [Python environment](https://github.com/NREL/T3CO_Go/blob/main/docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO_Go`) and run:

```bash
pip install t3co-go
install_demo_inputs
```

This installs the tool from PyPI and copies T3CO demo input files to the current folder

### Installation Source #2: From a git clone of the repository

T3CO-Go can also be installed from a clone of the [GitHub repository](https://github.com/NREL/T3CO_Go).

First, [clone](https://git-scm.com/docs/git-clone) the repository from [GitHub](https://github.com/NREL/T3CO_Go) from your desired directory (eg., /Users/Projects/):

```bash
git clone https://github.com/NREL/T3CO_Go.git T3CO_Go
```

This creates a git compliant folder 'T3CO_Go' (i.e., a '/Users/Projects/T3CO_Go' folder)

From within the [Python environment](https://github.com/NREL/T3CO_Go/blob/main/docs/installation.md#setting-up-env), navigate to the parent directory containing the T3CO repository (`cd T3CO_Go`) and run this command:

```bash
pip install -e .
install_demo_inputs
```

This installs the tool from the repo clone and copies T3CO demo input files to the same folder

Check that the right version of t3co_go is installed in your environment:

```bash
pip show t3co_go
```

If there are updates or new releases to t3co_go that don't show in the local version, use a `git pull` command the latest version from the `main` branch on the repo:

```bash
git pull origin main
```

## Starting a T3CO-Go instance

After installing T3CO_Go within a Python environment using one of the two sources, run this command:

```bash
run_t3co_go
```

This will open a web browser tab with T3CO prepared to run on your local machine in the background.

## Running your first analysis

To learn about the tool and run your first t3co_go analysis, proceed to the [Quick Start Guide](./quick_start.md)
