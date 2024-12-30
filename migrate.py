import sys
from migration import create_JSON_db, load_JSON_db

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'create':
        create_JSON_db()
    elif command == 'load':
        if len(sys.argv) < 3:
            print("Usage: python migrate.py load <file_name>")
            sys.exit(1)
        file_name = sys.argv[2]
        load_JSON_db(file_name)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, load")
        sys.exit(1)

