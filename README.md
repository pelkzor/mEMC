# mEMC

## Prerequisites

- Python 3.12

#### Python Packages

The required Python packages for this application are listed in the file `pyproject.toml`. To install these packages, run:

```bash
# Switch to / install Python 3.12 first
pip install uv
uv sync
```

Pip along with uv will download and install each package in `pyproject.toml` and its dependencies.

### Environment Variables
For the application to work properly regardless of where it is ran from, environment variables must be set up. A `.env` file has to be created in the root of the repository in. Populate it with the following:
```bash
# In .env
# Instrument IP
IP_ADDRESS=192.168.0.1
# To preselect all comboboxes and the simulator instrument on start for quicker debug cycles
SIMULATOR_MODE=TRUE
# Default folder where the application will save the results
WORKING_DIR=PATH_TO_WORKING_DIR
```

## Usage
With the packages installed and the environment variable(s) set up, run:

```bash
# From root/
uv run main.py
```

## Continuous development
If more packages are installed during development, `pyproject.toml` needs to be updated. Run the command below to update the file:

```bash
uv add <package-name>
```
