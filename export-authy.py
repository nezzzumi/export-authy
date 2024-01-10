import sys
from authy import Authy, AuthyInstallationNotFound, AuthyNotFound, SecretsNotFound
import argparse


parser = argparse.ArgumentParser(prog=sys.argv[0])

option_group = parser.add_mutually_exclusive_group(required=True)
option_group.add_argument(
    "-i",
    "--install",
    help="install a specific version of Authy (needed to export)",
    action="store_true",
)
parser.add_argument(
    "-f",
    "--force",
    help="force download and installation",
    action="store_true",
    default=False,
)
option_group.add_argument(
    "-e",
    "--export",
    help="export secrets as json",
    action="store_true",
)
option_group.add_argument(
    "-d",
    "--dump",
    help="dump secrets to stdout",
    action="store_true",
)
option_group.add_argument(
    "-r",
    "--revert",
    help="re-enable the updater",
    action="store_true",
)

args = parser.parse_args()


authy = Authy()

try:
    if args.install:
        authy.install_authy(force=args.force)
    elif args.export:
        authy.export()
    elif args.dump:
        authy.print_secrets()
    elif args.revert:
        authy.recover_updater()
        print("[i] Update.exe has been recovered")
except (AuthyNotFound, AuthyInstallationNotFound, SecretsNotFound) as e:
    print(f"[x] {e}")
