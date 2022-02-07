#!/usr/bin/env python3
"""Takes a file containing a list of directories under the PACS root, runs
through tar and then through 7za for AES256 encryption
"""
# TODO(rkm 2021-01-19) Thread-safe password file access/update
# TODO(rkm 2021-01-19) Allow specifying output directory
# TODO(rkm 2021-04-27) Re-add single-file mode
import argparse
import datetime
import logging
import os
import random
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import List
from typing import Tuple


PACS_ROOT = Path("/PACS")
assert PACS_ROOT.is_dir(), f"{PACS_ROOT} not found"

OUT_DIR = Path("/for_export")
assert OUT_DIR.is_dir(), f"{OUT_DIR} not found"

LOGS_DIR = Path("/logs")
LOGS_DIR.mkdir(exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
LOG_HANDLERS: List[logging.Handler] = [
    logging.FileHandler(LOGS_DIR / f"{Path(__file__).stem}-{NOW}.log"),
]

if sys.stdout.isatty():
    LOG_HANDLERS.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=LOG_HANDLERS,
)

# TODO(rkm 2021-02-18) Hardcoded file length
_EXPECTED_FILE_NAME_LENGTH = 35


def _log_disk_usage(input_files: Tuple[Path]) -> None:

    escaped_root = str(PACS_ROOT).replace("/", r"\/")
    cmd = (
        rf"sed 's/^/{escaped_root}\//g' {' '.join((str(x) for x in input_files))} "
        r"| xargs -s2091735 -d \\n du -sch"
    )

    try:
        stdout_b = subprocess.check_output(
            cmd,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        logging.exception(f"du command failed {e}")
        return

    stdout = stdout_b.decode().splitlines()
    assert stdout, "No stdout lines"
    total = stdout[-1].split("\t")[0]

    logging.info(f"du reports size of directory list as {total}")


def main() -> int:

    logging.info(f"Starting on {os.uname()[1]}")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "password_file",
        type=Path,
        help="The file to read a random password from",
    )
    parser.add_argument(
        "first_dir_list",
        type=Path,
        help=(
            "First file to read a directory list from. Directories must be "
            "relative to the PACS root"
        ),
    )
    parser.add_argument(
        "second_dir_list",
        type=Path,
        help=(
            "Second file to read a directory list from. Directories must be "
            "relative to the PACS root"
        ),
    )
    args = parser.parse_args()

    input_files = (args.first_dir_list, args.second_dir_list)

    assert all(x.is_file() for x in input_files), (
        "Could not find one of the specified input files: "
        f"{', '.join([str(x) for x in input_files])}"
    )
    assert input_files[0] != input_files[1], "Expected two different files"
    prefixes = {x.stem[: _EXPECTED_FILE_NAME_LENGTH - 2] for x in input_files}
    assert 1 == len(
        prefixes,
    ), f"Expected both input files to have a common prefix, got: {', '.join(prefixes)}"
    (prefix,) = prefixes
    assert _EXPECTED_FILE_NAME_LENGTH - 2 == len(prefix), (
        "Expected a common input file name of length "
        f"{_EXPECTED_FILE_NAME_LENGTH}, got: {len(prefix)}"
    )

    postfixes = [x.stem[_EXPECTED_FILE_NAME_LENGTH - 2 :] for x in input_files]
    out_file_name = f"{prefix}{postfixes[0]}_{postfixes[1]}.7z"
    out_filepath = Path(out_file_name)
    if out_filepath.is_file():
        logging.error(f"Output file '{out_filepath}' already exists")
        return 1

    assert args.password_file.is_file(), f"{args.password_file} not found"
    with open(args.password_file) as f:
        lines = f.read().splitlines()

    assert lines, "No passwords left in file"
    password = random.choice(lines)
    del lines[lines.index(password)]

    with open(args.password_file, "w") as f:
        f.writelines([x + "\n" for x in lines])

    logging.info("Removed password from file")

    # TODO(rkm 2021-01-19) Handle any exceptions here
    logging.info("Starting thread to measure disk usage")
    thread = threading.Thread(
        target=_log_disk_usage,
        args=(input_files,),
    )
    thread.start()

    logging.info(f"Will create '{out_filepath}' with password '{password}'")

    tar_files = " ".join(f"-T {x}" for x in input_files)
    cmd: str = (
        f"tar cO -C {PACS_ROOT.resolve()} {tar_files} --owner=0 --group=0 "
        f"| pigz --best --recursive "
        f"| 7za a '-p{password}' -si -t7z -mx=1 -mhe {out_filepath.resolve()}"
    )
    logging.info(cmd)

    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    thread.join()

    if proc.returncode:
        logging.error(
            f"\nSTDOUT:\n{proc.stdout.decode()}\nSTDERR:\n{proc.stderr.decode()}",
        )
        return 1

    final_output_path = OUT_DIR / out_file_name
    if final_output_path.is_file():
        logging.error(f"Output file '{final_output_path}' already exists. Not copying")
        return 1

    # TODO(rkm 2021-04-27) Enable this as a switch
    # logging.info("Copying file to backup directory")
    # shutil.copy2(str(out_filepath.resolve()), str(BACKUP_DIR))

    logging.info("Moving file to output directory and setting permissions")
    shutil.move(str(out_filepath.resolve()), str(OUT_DIR))
    os.chmod(final_output_path, 0o440)

    # TODO(rkm 2021-04-27) Add md5sum here

    logging.info("Completed successfully")
    return 0


if __name__ == "__main__":
    exit(main())
