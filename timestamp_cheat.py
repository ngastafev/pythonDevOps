import os
import time
import argparse
from datetime import datetime


def sync_timestamps(source_path, target_path):
    stat_info = os.stat(source_path)
    os.utime(target_path, (stat_info.st_atime, stat_info.st_mtime))
    print(f"Timestamps copied from '{source_path}' to '{target_path}'")


def set_timestamp_manually(file_path, timestamp_str, attr='both'):
    dt = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
    timestamp = dt.timestamp()

    stat_info = os.stat(file_path)
    if attr == 'both':
        os.utime(file_path, (timestamp, timestamp))
    elif attr == 'mtime':
        os.utime(file_path, (stat_info.st_atime, timestamp))
    elif attr == 'atime':
        os.utime(file_path, (timestamp, stat_info.st_mtime))

    print(f"Set timestamp(s) on '{file_path}' to {dt.isoformat()}")


def main():
    parser = argparse.ArgumentParser(description="Sync file timestamps.")
    parser.add_argument("-s", "--source", help="Source file")
    parser.add_argument("-t", "--target", required=True, help="Target file")
    parser.add_argument("--set-time", help="Set time manually (ISO format: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--attr", choices=['both', 'mtime', 'atime'], default='both', help="Which timestamp to set")

    args = parser.parse_args()

    if args.source:
        if not os.path.exists(args.source):
            print(f"Source file does not exist: {args.source}")
            return
        sync_timestamps(args.source, args.target)
    elif args.set_time:
        set_timestamp_manually(args.target, args.set_time, args.attr)
    else:
        with open(args.target, 'a'):
            os.utime(args.target, None)
        print(f"Touched '{args.target}', updated to current time.")


if __name__ == "__main__":
    main()