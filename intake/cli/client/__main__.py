import sys
import argparse

from intake.catalog import load_catalog


def print_entry_info(catalog, name):
    info = catalog.describe(name)
    for key in sorted(info.keys()):
        print("[{}] {}={}".format(name, key, info[key]))


def listing(args):
    catalog = load_catalog(args.uri)
    for entry in catalog.list():
        if args.full:
            print_entry_info(catalog, entry)
        else:
            print(entry)


def describe(args):
    catalog = load_catalog(args.uri)
    print_entry_info(catalog, args.name)


def exists(args):
    catalog = load_catalog(args.uri)
    try:
        catalog.describe(args.name)
        print(True)
    except:
        print(False)


def get(args):
    catalog = load_catalog(args.uri)
    with catalog.get(args.name) as f:
        print(f.read())


def discover(args):
    catalog = load_catalog(args.uri)
    with catalog.get(args.name) as f:
        print(f.discover())


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='Intake Catalog CLI', add_help=False)
    subparsers = parser.add_subparsers(help='sub-command help')

    list_parser = subparsers.add_parser('list', help='catalog listing')
    list_parser.add_argument('--full', action='store_true')
    list_parser.add_argument('uri', metavar='URI', type=str, help='Catalog URI')
    list_parser.set_defaults(func=listing)

    describe_parser = subparsers.add_parser('describe', help='description for catalog entry')
    describe_parser.add_argument('uri', metavar='URI', type=str, help='Catalog URI')
    describe_parser.add_argument('name', metavar='NAME', type=str, help='Catalog name')
    describe_parser.set_defaults(func=describe)

    exists_parser = subparsers.add_parser('exists', help='existence check for catalog entry')
    exists_parser.add_argument('uri', metavar='URI', type=str, help='Catalog URI')
    exists_parser.add_argument('name', metavar='NAME', type=str, help='Catalog name')
    exists_parser.set_defaults(func=exists)

    get_parser = subparsers.add_parser('get', help='get catalog entry')
    get_parser.add_argument('uri', metavar='URI', type=str, help='Catalog URI')
    get_parser.add_argument('name', metavar='NAME', type=str, help='Catalog name')
    get_parser.set_defaults(func=get)

    discover_parser = subparsers.add_parser('discover', help='discover catalog entry')
    discover_parser.add_argument('uri', metavar='URI', type=str, help='Catalog URI')
    discover_parser.add_argument('name', metavar='NAME', type=str, help='Catalog name')
    discover_parser.set_defaults(func=discover)

    if not argv[1:]:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
