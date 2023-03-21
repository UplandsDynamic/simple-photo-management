import os
import subprocess
from difPy import dif


class FotoToolz:

    """
    main class to run the processes
    """

    def __init__(
            self, directory, fix_filenames=False, detect_dupes=False, change_permissions=False, dupe_search_dirs=[],
            file_chars_to_replace=(),
            dir_chars_to_replace=(),
            new_char="",
            results_file="",
            log_full_path=True,
            verbose=False):
        self.file_chars_to_replace = file_chars_to_replace
        self.dir_chars_to_replace = dir_chars_to_replace
        self.new_char = new_char
        self.change_permissions = change_permissions
        self.results_file = results_file
        self.log_full_path = log_full_path
        self.verbose = verbose
        self.filename_fixer(directory) if fix_filenames else None
        self.dupe_detector(directory, dupe_search_dirs) if detect_dupes else None

    def filename_fixer(self, directory):
        """
        renames all files in dirs, recursively,
        replacing char_to_replace with new_char
        """
        change_counter = 0
        try:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    fn = old = file
                    for char in self.file_chars_to_replace:
                        fn = fn.replace(char, self.new_char)
                    if old != fn:
                        print(f"Name of file {old} changed to {fn}\n") if self.verbose else None
                    new_file_path = os.path.join(directory, fn)
                    os.rename(file_path, new_file_path)
                    change_counter += 1
                elif os.path.isdir(file_path):
                    dn = old = file
                    for char in self.dir_chars_to_replace:
                        dn = dn.replace(char, self.new_char)
                    if old != dn:
                        print(f"Name of directory {old} changed to {dn}\n") if self.verbose else None
                    new_dir = os.path.join(directory, dn)
                    os.rename(file_path, new_dir)
                    self.filename_fixer(new_dir)
        except PermissionError as e:
            print(f"Do not have permission to access {directory} - skipping.") if self.verbose else None

    def dupe_detector(self, img_dir, search_dirs):
        locations = set()

        def extract_locations(data):
            if isinstance(data, dict):
                if 'location' in data:
                    locations.add(data['location'])
                for value in data.values():
                    extract_locations(value)
            elif isinstance(data, list):
                for item in data:
                    extract_locations(item)

        def file_writer(file_path):
            with open(self.results_file, "a+") as file:
                file.seek(0)
                data = file.read(100)
                if len(data) > 0:
                    file.write("\n")
                else:
                    file.write("# These image files were not added to the system\n\n")
                file.write(os.path.abspath(file_path)) if self.log_full_path else file.write(
                    os.path.basename(os.path.abspath(file_path)))

        print(
            f"\nSearching these directories for duplicates:\n" + "\n".join([os.path.abspath(d) for d in search_dirs]) +
            "\n\n") if self.verbose else None
        search = dif(search_dirs, similarity='duplicates', fast_search=True)
        extract_locations(search.result)
        print(f"\nDuplicated images: \n" + "\n".join([os.path.abspath(l) for l in locations])) if self.verbose else None
        if self.change_permissions:
            # loop through each file in the set
            for file_path in locations:
                # only change file permissions if the file path includes the directory being assessed
                if os.path.abspath(img_dir) in os.path.abspath(os.path.dirname(file_path)):
                    # use subprocess to run the chmod command and change the file permissions to 000
                    subprocess.run(["chmod", "000", file_path])
                    print(f"Changed permissions of file {file_path} to 000.") if self.verbose else None
                    # write paths of dupes with modified file permissions to results file
                    file_writer(file_path)
                else:
                    print(
                        f"Not touching file {os.path.abspath(file_path)} as it is not in {os.path.abspath(img_dir)}\n\n") if self.verbose else None


# driver
if __name__ == "__main__":
    directory = "./rename_test"  # directory being scanned - permissions CAN be changed
    dupe_search_dirs = ["../../photo_directory", "./rename_test"]  # directories to search - permissions NOT changed
    file_chars_to_replace = (" ", "(", ")", "[", "]", "'", "&", ",")
    dir_chars_to_replace = (" ", "(", ")", "[", "]", ".", "'", "&", ",")
    new_char = "_"
    results_file = "results.txt"
    log_full_path = True
    fix_filenames = True
    detect_dupes = True
    change_permissions = True
    verbose = False

    FotoToolz(
        directory=directory, fix_filenames=fix_filenames, detect_dupes=detect_dupes,
        change_permissions=change_permissions, dupe_search_dirs=dupe_search_dirs,
        file_chars_to_replace=file_chars_to_replace, dir_chars_to_replace=dir_chars_to_replace, new_char=new_char,
        results_file=results_file, log_full_path=log_full_path, verbose=verbose)
    print("Job done!")
