import re, subprocess, datetime

"""
Script to tag photos where previous attempt 
had failed due to the specified 'Error: Exiv2 exception'
error, as observed in the log file.
"""


def identify_tags(log_url):
    to_write = dict()
    line_before = ""
    with open(log_url) as f:
        for line in f:
            if "Error: Exiv2 exception" in line:
                # print("\nStarting new line ...")
                find_url = re.search("(?=.+?)(?=\/)(.+)(?=\:)", line)
                if find_url:
                    # print(f"Found URL: {find_url.group(1)}")
                    url = find_url.group(1)
                    unwritten = re.search(
                        "(?:.+\[(?:\"|'))(.+)(?:(?:\"|')\].*)", line_before
                    )
                    tag = unwritten.group(1) if unwritten else None
                    # print(f"Found previously unwritten tag: '{tag}'")
                    if tag:
                        if url in to_write:
                            # print(f"Found current tags: {to_write[url]}")
                            to_write[url].append(tag)
                            # print(f"Updated {url} - it will now get these tags: {to_write[url]}")
                        else:
                            # print(f"Will write '{tag}' to {url}")
                            to_write[url] = [tag]
                    else:
                        pass
                        # print(f"ERROR: These tags were not added: {line_before} for this error line: {error_line.group(1)}")
            line_before = line
    return remove_dupes(to_write)


def remove_dupes(photos_to_write):
    for url, tags in photos_to_write.items():
        photos_to_write[url] = list(set(tags))
    return photos_to_write


def write_tags(photos_to_write):
    for url, new_tags in photos_to_write.items():
        # read existing tags from photo
        read_tags = subprocess.run(
            ["exiv2", "-PIt", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if read_tags.stderr:
            with open("photophixer.log", "a") as f:
                f.write(
                    f"{datetime.datetime.utcnow()} - ERROR - An error occurred whilst reading existing tags for {url}: {read_tags.stderr.strip()}. Writing new tags abandoned.\n\n"
                )
        else:
            # add new tags to existing
            existing_tags = list(filter(None, read_tags.stdout.strip().split("\n")))
            # print(existing_tags)
            new_tags = (
                list(set((new_tags + existing_tags))) if existing_tags else new_tags
            )
            # clear old tags, to write new refreshed list (no dupes)
            delete = subprocess.run(
                ["exiv2", "-M", f"del Iptc.Application2.Keywords String", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if delete.stderr:
                with open("photophixer.log", "a") as f:
                    f.write(
                        f"{datetime.datetime.utcnow()} - ERROR - An error occurred whilst deleting tags for {url}: {delete.stderr.strip()}. Writing new tags abandoned.\n\n"
                    )
            else:
                # write new tags to photo
                for tag in new_tags:
                    write = subprocess.run(
                        [
                            "exiv2",
                            "-M",
                            f"add Iptc.Application2.Keywords String {tag}",
                            url,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                    )
                    if write.stderr:
                        with open("photophixer.log", "a") as f:
                            f.write(
                                f"{datetime.datetime.utcnow()} - ERROR - An error occurred while writing '{tag}' to {url}: {write.stderr.strip()}\n\n"
                            )
    print("Job done!")


def main():
    photos_to_write = identify_tags(log_url="spm_2023.log")
    write_tags(photos_to_write)


if __name__ == "__main__":
    main()
