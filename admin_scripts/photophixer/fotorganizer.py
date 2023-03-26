import argparse
import subprocess
import json
import re
from pathlib import Path
import shutil

global _verbose_output


def _v(message: str):
    global _verbose_output
    print(f"{message}\n") if _verbose_output else None


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
    for f in file_paths:
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
    return results


def _find_years(files: list) -> list[dict]:
    results: list = []
    pattern = r"(?i)date.*(\d{4}?)"
    for f in files:
        for tag in f["tags"]:
            match = re.search(pattern, tag, re.IGNORECASE)
            results.append({
                "file_path": f["file_path"],
                "year": match.group(1) if match is not None else None,
                "errors": ""
            })
    return results


def _move_images(images: list, root_dir: str) -> list[dict]:
    successful: list[dict] = []
    errors: list[dict] = []
    for img in images:
        try:
            target_dir: Path = Path(f"{root_dir}/{img['year']}") if img["year"] else Path(f"{root_dir}/no_year")
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                new_path: str = shutil.move(img['file_path'], target_dir)
                successful.append({"new_filepath": new_path, "old_filepath": img["file_path"]})
            except shutil.Error as e:
                _v("File already exists as this path. Not moving.")
        except Exception as e:
            errors.append({"old_filepath": img["file_path"], "error": str(e)})
    return successful, errors


def _format_json(input: list):
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


def execute(root_dir: str, verbose: True):
    global _verbose_output
    _verbose_output = verbose
    _accepted_filetypes = ("jpg", "jpeg", "tif", "tiff", "png")
    newline: str = "\n"
    try:
        _validate_directory(root_dir)
        root_dir = Path(root_dir).resolve(strict=True)
        found_paths, excluded_paths = _get_files(root_dir, _accepted_filetypes)
        results = _get_tags(found_paths)
        years = _find_years(files=results)
        moved, move_failed = _move_images(years, root_dir)
        print(_format_json(moved))
        print(_format_json(move_failed))
        # print stuff
        _v(f"{len(found_paths)} files were found in or under {root_dir}.{newline}")
        _v(f"{len(excluded_paths)} files were excluded in or under {root_dir}.{newline}")
        _v(f"Here is the list of found files: {newline}{f'{newline}'.join([str(f) for f in found_paths])}")
        _v(f"Here is the list of excluded files: {newline}{f'{newline}'.join([str(f) for f in excluded_paths])}")
        _v(_format_json(results))
        _v(_format_json(years))
    except FileNotFoundError as e:
        print("Root directory was not found. Aborting attempt.")
    except ValueError as e:
        print(str(e))


# driver
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move all image files with dates in their IPTC tag comments into date-titled folders")
    parser.add_argument('-d', '--directory', type=str, help='Root image directory. Full path required', required=True)
    args = parser.parse_args()
    confirm = input(f"Your selected directory was {args.directory}.\nPlease confirm (Y)es, (N)o: ")
    execute(root_dir=args.directory, verbose=False) if confirm.lower() in ("yes", "y") else print("Aborting.")
