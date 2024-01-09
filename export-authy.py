import sys
from authy import Authy
import argparse


parser = argparse.ArgumentParser(prog=sys.argv[0])
parser.add_argument(
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
parser.add_argument(
    "-e",
    "--export",
    help="export secrets",
    action="store_true",
)

args = parser.parse_args()

if not args.install or args.export:
    parser.print_help()
    exit()

authy = Authy()

if args.install:
    authy.install_authy(force=args.force)
elif args.export:
    ...
