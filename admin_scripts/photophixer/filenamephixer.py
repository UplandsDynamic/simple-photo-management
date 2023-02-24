import os


"""
renames all files in directories, recursively, 
replacing char_to_replace with new_char
"""


def rename(dir, file_chars_to_replace, dir_chars_to_replace, new_char):
    change_counter = 0
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            fn = old = file
            for char in file_chars_to_replace:
                fn = fn.replace(char, new_char)
            if old != fn:
                print(f"Name of file {old} changed to {fn}\n")
            new_file_path = os.path.join(dir, fn)
            os.rename(file_path, new_file_path)
            change_counter += 1
        elif os.path.isdir(file_path):
            dn = old = file
            for char in dir_chars_to_replace:
                dn = dn.replace(char, new_char)
            if old != dn:
                print(f"Name of directory {old} changed to {dn}\n")
            new_dir = os.path.join(dir, dn)
            os.rename(file_path, new_dir)
            rename(new_dir, file_chars_to_replace, dir_chars_to_replace, new_char)


# driver
if __name__ == "__main__":
    root_dir = "/mnt/aninstancedatacenter/family-history-spm-testing/IMAGE_ARCHIVE"
    file_chars_to_replace = (" ", "(", ")", "[", "]", "'", "&")
    dir_chars_to_replace = (" ", "(", ")", "[", "]", ".", "'", "&")
    rename(
        dir=root_dir,
        file_chars_to_replace=file_chars_to_replace,
        dir_chars_to_replace=dir_chars_to_replace,
        new_char="_",
    )
    print("Job done!")
