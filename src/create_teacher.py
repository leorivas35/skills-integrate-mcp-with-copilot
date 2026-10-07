import getpass
import json
import os
import sys

from app import TEACHERS_FILE, create_password_hash


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print("Usage: python src/create_teacher.py <username>", file=sys.stderr)
        return 2

    username = sys.argv[1].strip()
    password = getpass.getpass("Teacher password (12+ characters): ")
    if len(password) < 12:
        print("Password must be at least 12 characters.", file=sys.stderr)
        return 2

    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 2

    try:
        data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {"teachers": []}
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read teacher credentials: {error}", file=sys.stderr)
        return 1

    if not isinstance(data, dict) or not isinstance(data.get("teachers"), list):
        print("Teacher credentials file has an invalid format.", file=sys.stderr)
        return 1
    if any(teacher.get("username") == username for teacher in data["teachers"]):
        print("That teacher username already exists.", file=sys.stderr)
        return 1

    salt, password_hash = create_password_hash(password)
    data["teachers"].append({
        "username": username,
        "salt": salt,
        "password_hash": password_hash,
    })
    TEACHERS_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(TEACHERS_FILE, 0o600)
    print(f"Teacher account created for {username}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())