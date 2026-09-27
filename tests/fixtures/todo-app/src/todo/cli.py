import argparse
from datetime import date

from todo import store
from todo.due import parse_due


def main(argv=None):
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--due")
    add.add_argument("--priority", type=int, default=2)

    lst = sub.add_parser("list")
    lst.add_argument("--all", action="store_true")
    lst.add_argument("--due-before")

    done = sub.add_parser("done")
    done.add_argument("id", type=int)

    args = parser.parse_args(argv)
    if args.command == "add":
        if args.due:
            parse_due(args.due)
        store.add_item(args.title, args.due, args.priority)
    elif args.command == "list":
        for item in store.load():
            if item["done"] and not args.all:
                continue
            if args.due_before and (not item["due"] or parse_due(item["due"]) >= parse_due(args.due_before)):
                continue
            print(f"{item['id']}. {item['title']}")
    elif args.command == "done":
        store.mark_done(args.id)
