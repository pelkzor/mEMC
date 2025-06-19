# mEMC

## Prerequisites

- Python 3.12

#### Python Packages

The required Python packages for this application are listed in the file `requires.txt`. To install these packages, run:

```bash
# Switch to / install Python 3.12 first
python -m venv .venv
pip install -r requires.txt
```

Pip will download and install each package in `requires.txt` and its dependencies.

### Environment Variables
For the application to work properly regardless of where it is ran from, environment variables must be set up. A `.env` file has to be created in the root of the repository in. Populate it with the following:
```bash
# In .env
IP_ADDRESS=IP_OF_LOCAL_MACHINE
```

## Usage
With the packages installed and the environment variable(s) set up, run:

```bash
# From root/
python -m main
```

## Continous development
If more packages are installed during development, `requires.txt` needs to be updated. Run the command below to update the file:

```bash
pip freeze > requires.txt
```
