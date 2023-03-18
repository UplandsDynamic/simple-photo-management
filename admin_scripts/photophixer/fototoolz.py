import os
import subprocess
from difPy import dif


class FotoToolz:

    """
    main class to run the processes
    """

    def __init__(
            self, directory, fix_filenames=False, detect_dupes=False, dupe_search_dirs=[],
            file_chars_to_replace=(),
            dir_chars_to_replace=(),
            new_char=""):
        self.file_chars_to_replace = file_chars_to_replace
        self.dir_chars_to_replace = dir_chars_to_replace
        self.new_char = new_char
        self.filename_fixer(directory) if fix_filenames else None
        self.dupe_detector(directory, dupe_search_dirs) if detect_dupes else None

    def filename_fixer(self, directory):
        """
        renames all files in dirs, recursively,
        replacing char_to_replace with new_char
        """
        change_counter = 0
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                fn = old = file
                for char in self.file_chars_to_replace:
                    fn = fn.replace(char, self.new_char)
                if old != fn:
                    print(f"Name of file {old} changed to {fn}\n")
                new_file_path = os.path.join(directory, fn)
                os.rename(file_path, new_file_path)
                change_counter += 1
            elif os.path.isdir(file_path):
                dn = old = file
                for char in self.dir_chars_to_replace:
                    dn = dn.replace(char, self.new_char)
                if old != dn:
                    print(f"Name of directory {old} changed to {dn}\n")
                new_dir = os.path.join(directory, dn)
                os.rename(file_path, new_dir)
                self.filename_fixer(new_dir)

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
        print(
            f"\nSearching these directories for duplicates:\n" + "\n".join([os.path.abspath(d) for d in search_dirs]) +
            "\n\n")
        search = dif(search_dirs, similarity='duplicates')
        extract_locations(search.result)
        print(f"\nDuplicated images: \n" + "\n".join([os.path.abspath(l) for l in locations]))
        # loop through each file in the set
        for file_path in locations:
            # only change file permissions if the file path includes the directory named "batch"
            if os.path.abspath(img_dir) in os.path.abspath(os.path.dirname(file_path)):
                # use subprocess to run the chmod command and change the file permissions to 000
                subprocess.run(["chmod", "000", file_path])
                print(f"Changed permissions of file {file_path} to 000.")
            else:
                print(f"Not touching file {os.path.abspath(file_path)} as it is not in {os.path.abspath(img_dir)}\n\n")


# driver
if __name__ == "__main__":
    directory = ""
    dupe_search_dirs = []
    file_chars_to_replace = (" ", "(", ")", "[", "]", "'", "&")
    dir_chars_to_replace = (" ", "(", ")", "[", "]", ".", "'", "&")
    new_char = "_"
    FotoToolz(directory=directory, fix_filenames=True, detect_dupes=False,
              dupe_search_dirs=dupe_search_dirs, file_chars_to_replace=file_chars_to_replace,
              dir_chars_to_replace=dir_chars_to_replace, new_char=new_char)
    print("Job done!")
