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

## Installing t3co_go Python Package

t3co_go is available on PyPI and as a public access GitHub repository. This gives the user two ways of installing the t3co_go Python Package.

### 1. Installing From [PyPI](https://pypi.org/project/t3co_go/) <a name=install-from-pypi></a>

t3co_go can be easily installed from PyPI. This is the preferred method when using t3co_go to run analysis using input files. To install the latest release:

```bash
pip install t3co_go
```

To install a specific version (for example t3co_go v0.1.0):

```bash
pip install t3co_go==0.1.0
```

### 2. From [GitHub](https://github.com/NREL/t3co_go)

t3co_go can also be installed directly from the GitHub repository for accessing demo input files and running t3co_go using the Command Line Interface.

First, [clone](https://git-scm.com/docs/git-clone) the repository from [GitHub](https://github.com/NREL/t3co_go):

```bash
git clone https://github.nrel.gov/AVCI/t3co_go.git t3co_go
```

From within the [Python environment](#setting-up-env) Navigate to the parent directory containing the t3co_go repository e.g. `cd GitHub/t3co_go/` and run:

```bash
pip install -e .
```

This installs the local version of the t3co_go clone along with all its [dependencies](https://github.nrel.gov/AVCI/t3co_go/blob/3ab424fec5c24ca0bcf7e0983aa72b781ab60a23/requirements.txt).

Check that the right version of t3co_go is installed in your environment:

```bash
pip show t3co_go
```

If there are updates or new releases to t3co_go that don't show in the local version, use a `git pull` command the latest version from the `main` branch on the repo:

```bash
git pull origin main
```

## Copying T3CO-Go Demo Input Files <a name=copy-demo-inputs></a>

The `t3co_go.resources` folder contains all the necessary input files needed for running t3co_go. However, it sometimes is difficult to navigate to these files when installing. To help with this, run this command on the Command Line Interface.

```bash
install_t3co_go_demo_inputs
```

The user will receive these questions on the command line:

`Do you want to copy the t3co_go demo input files? (y/n):`

`Enter the path where you want to copy demo input files:`

Choose `y` and provide the desired destination path to get a `demo_inputs` folder containing the `t3co_go.resources` files copied to your local directory.

## Starting a T3CO-Go instance

After installing T3CO_Go within a Python environment using one of the two sources, run this command:

```bash
run_t3co_go
```

This will open a web browser tab with T3CO prepared to run on your local machine in the background.

## Running your first analysis

To learn about the tool and run your first t3co_go analysis, proceed to the [Quick Start Guide](./quick_start.md)
