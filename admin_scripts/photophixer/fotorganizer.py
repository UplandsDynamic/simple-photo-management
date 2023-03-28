import argparse
import subprocess
import json
import re
import shutil
import uuid
from math import floor
from distutils.util import strtobool
from pathlib import Path
from datetime import datetime

global _verbose_output


def _v(message: str) -> None:
    global _verbose_output
    print(f"{message}", end="\n\n") if _verbose_output else None
    _write_log(message)


def _get_files(root_dir: Path, accepted_filetypes: tuple) -> tuple:
    found_paths = [p for p in root_dir.rglob("*") if p.is_file()]
    valid_paths = []
    excluded_paths = []
    accepted_filetypes = [f.lower() for f in accepted_filetypes]
    for p in found_paths:
        if p.suffix.lower().strip(".") in accepted_filetypes:
            valid_paths.append(p)
        else:
            excluded_paths.append(p)
    return valid_paths, excluded_paths


def _get_tags(file_paths: list[Path]) -> list[dict]:
    results: list = []
    print("Reading tags...")
    for idx, f in enumerate(file_paths):
        tags: list = []
        read = subprocess.run(
            ["exiv2", "-PI", f],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        meta_data = read.stdout.splitlines()
        for item in meta_data:
            item_data = item.split()
            tags.append(" ".join(item_data[3:]))
        results.append({
            "file_path": f,
            "tags": tags,
            "errors": read.stderr
        })
        _show_progress(idx, len(file_paths))
    print("\nTask complete.", end="\n\n")
    return results


def _find_years(files: list) -> list[dict]:
    results: list = []
    pattern = r"(?i)date.*(\d{4}?)"
    for f in files:
        for tag in f["tags"]:
            match = re.search(pattern, tag, re.IGNORECASE)
            if match:
                break
        results.append({
            "file_path": f["file_path"],
            "year": match.group(1) if match else None,
            "errors": ""
        })
    return results


def _move_images(images: list, root_dir: Path, rename_files: bool) -> tuple(list[dict]):
    successful: list[dict] = []
    errors: list[dict] = []
    print("Moving images...")
    for idx, img in enumerate(images):
        try:
            target_dir: Path = root_dir / Path(img["year"]) if img["year"] else root_dir / Path("no_year")
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                new_path: Path = Path(shutil.move(
                    img["file_path"],
                    target_dir / _gen_filename(img["file_path"].suffix) if rename_files else target_dir)).resolve()
                successful.append({"new_filepath": new_path, "old_filepath": img["file_path"]})
            except shutil.Error as e:
                _v("File already exists as this path. Not moving.")
        except Exception as e:
            errors.append({"old_filepath": img["file_path"], "error": str(e)})
        _show_progress(idx, len(images))
    print("\nTask complete.", end="\n\n")
    return successful, errors


def _gen_filename(suffix: str) -> Path:
    return Path(str(uuid.uuid4()) + suffix)


def _show_progress(current: int, total: int) -> None:
    print(f"Progress: [{current}/{total}][{floor((current/total)*100)}%]", end="\r", flush=True)


def _format_json(input: list) -> list[dict]:
    for r in input:
        if "file_path" in r:
            r["file_path"] = str(r["file_path"])
        if "old_filepath" in r:
            r["old_filepath"] = str(r["old_filepath"])
        if "new_filepath" in r:
            r["new_filepath"] = str(r["new_filepath"])
    return json.dumps(input, indent=4, sort_keys=True)


def _validate_directory(arg: str) -> str:
    if arg[0] == "." or type(arg) is not str:
        raise ValueError("Invalid root path. Aborting attempt.")
    return arg


def _write_log(message: str) -> None:
    log_path = Path(".")
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path / "fotorganizer.log", "a+") as file:
        file.seek(0)
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        else:
            file.write("# Output log for the fotorganizer script.\n\n")
        file.write(f"\n{dt}   {message}")


def execute(root_dir: str, verbose: bool = False, rename_files: bool = False) -> None:
    global _verbose_output
    _verbose_output = verbose
    _accepted_filetypes = ("jpg", "jpeg", "tif", "tiff", "png")
    newline: str = "\n"
    try:
        _validate_directory(root_dir)
        root_dir = Path(root_dir).resolve(strict=True)
        print("Starting process...", end="\n\n")
        found_paths, excluded_paths = _get_files(root_dir, _accepted_filetypes)
        results = _get_tags(found_paths)
        years = _find_years(files=results)
        moved, move_failed = _move_images(years, root_dir, rename_files)
        # print / log stuff
        _v(f"{len(found_paths)} files were found in or under {root_dir}.")
        _v(f"{len(excluded_paths)} files were excluded in or under {root_dir}.")
        _v(
            f"List of found files: {newline}{f'{newline}'.join([str(f) for f in found_paths]) if found_paths else 'None'}")
        _v(
            f"List of excluded files: {newline}{f'{newline}'.join([str(f) for f in excluded_paths]) if excluded_paths else 'None'}")
        _v(f"Tags that were read: \n\n{_format_json(results)}")
        _v(f"Years that were detected: \n\n{_format_json(years)}")
        _v(f"Moved files: \n\n{_format_json(moved)}")
        _v(f"Failed moves: \n\n{_format_json(move_failed)}")
    except FileNotFoundError as e:
        print("Root directory was not found. Aborting attempt.")
    except ValueError as e:
        print(str(e))


# driver
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move all image files with dates in their ITPC tag comments into date-titled folders")
    parser.add_argument('-d', '--directory', type=str, help='Root image directory. Full path required', required=True)
    parser.add_argument('-v', '--verbose', type=lambda x: bool(strtobool(x)),
                        help='Print verbose output', required=False, choices=[True, False], default=False)
    parser.add_argument(
        '-rf', '--rename_files', type=lambda x: bool(strtobool(x)),
        help='Rename moved files', required=False, choices=[True, False], default=False)
    args = parser.parse_args()
    confirm = input(f"Your selected directory was {args.directory}.\nPlease confirm (Y)es, (N)o: ")
    execute(
        root_dir=args.directory, verbose=args.verbose, rename_files=args.rename_files) if confirm.lower() in (
        "yes", "y") else print("Aborting.")
