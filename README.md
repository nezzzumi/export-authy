## Export secrets from Authy

This script automates the process of dumping secrets from Authy.

It's useful for import them into another 2FA app.

## Installation

Clone this repo and install the dependencies.

> A [virtual environment](https://docs.python.org/3/library/venv.html) is recommended.

```bash
git clone https://github.com/nezzzumi/export-authy
cd export-authy/

python -m pip install -r requirements.txt
```

## Usage
```
usage: .\export-authy.py [-h] [-i] [-f] [-e] [-d] [-r]

options:
  -h, --help     show this help message and exit
  -i, --install  install a specific version of Authy (required for export/dump)
  -f, --force    force download and installation
  -e, --export   export secrets as json
  -d, --dump     dump secrets to stdout
  -r, --revert   re-enable the updater
```

First of all, you need to install the version of Authy that supports remote debbuging.

Use the `--install` flag for this.

    python export-authy.py -i

> When you open Authy, an auto-updater is opened in the background. To prevent the update, the script renames the updater in the Authy folder. To revert this operation, use the `--revert` option, or install a newest version of Authy.

You can now export/dump your secrets with the `-export` or `-dump` option.

    python export-authy.py -d

### References

-   [Export TOTP tokens from Authy](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93)
