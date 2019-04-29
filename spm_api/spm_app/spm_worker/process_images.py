#!/usr/bin/env python3
import glob
import os
import pyexiv2
from PIL import Image
import hashlib
from pathlib import Path
import glob

ORIGIN_IMAGE_PATHS = set(os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../test_images")}')))
PROCESSED_IMAGE_PATH = os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../test_images/processed")}'))
THUMB_PATH = os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../test_images/processed/tn")}'))
CONVERSION_FORMAT = 'jpg'


class ProcessImages:
    """
    Processes images by:
        - convert image format (e.g. .tif to .jpg)
        - read & transfer IPTC 'keyword' tags from original to converted image
    """
    ALLOWED_IMAGE_FORMATS = ['jpeg', 'jpg', 'tiff', 'tif', 'png']

    def __init__(self, origin_image_paths=None, origin_file_url=None, processed_image_path=None, thumb_path=None, conversion_format=None,
                 retag=False, process_single=False, tags=None):
        """
        initiate the class
        :param origin_image_paths: set of paths of dirs of photos to be converted and/or tagged
        :param origin_file_url: url of file to process, if processing single file rather than dir
        :param processed_image_path: path to save the processed image to
        :param conversion_format: file format to convert image to
        :param retag: boolean value, signifying whether to perform re-tagging
            if the image name already exists in the defined location where
            converted images are saved.
        :param process_single: boolean value, signifying whether to process a single file rather than a dir
        :param tags: dict of new tags to add, in form: {'iptc_key': iptc_key, 'tags': tags}
        Note: standardise on lowercase file extensions
        """
        self.ORIGIN_IMAGE_PATHS = origin_image_paths
        self.PROCESSED_IMAGE_PATH = processed_image_path
        self.THUMB_PATH = thumb_path
        self.CONVERSION_FORMAT = conversion_format.lower() \
            if conversion_format.lower() in self.ALLOWED_IMAGE_FORMATS else None
        self.retag = retag if isinstance(retag, bool) else False
        self.process_single = process_single
        self.origin_file_url = origin_file_url
        self.tags = tags

    @staticmethod
    def file_url_list_generator(directories: set, allowed_formats: list = None, recursive: bool = False,
                                containing_str: str = '') -> str:
        """
        generator method, to get full urls of all files in directories
        :param recursive: whether to scan recursively
        :param directories: set of directories in which to scan for files
        :param containing_str: string that included filenames must contain (if any)
        :return: yield file urls (str) from the generated list
        """
        file_urls = []
        match_pattern = f'**/*'
        if isinstance(directories, set):
            for index, directory in enumerate(directories):
                try:
                    if recursive:
                        if allowed_formats:
                            # produce <generator object>
                            url_list_generator = (Path(directory).glob(
                                f'{match_pattern}.{f.lower()}') for f in allowed_formats)
                            # produce [[], [PosixPath('/path/to/file.jpg')], []]
                            url_list = [list(x_file_type)
                                        for x_file_type in url_list_generator]
                            #produce ['/path/to/file.jpg', '/path2/to/file_2.jpg']
                            for urls_inner_list in url_list:
                                file_urls.extend([str(u)
                                                  for u in urls_inner_list])
                        else:
                            item_list = (
                                list(Path(directory).glob(match_pattern)))
                            file_urls.extend(
                                [str(i) for i in item_list if not os.path.isdir(i)])
                    else:
                        if allowed_formats:
                            file_urls.extend(list(os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[
                                1].strip('.') in allowed_formats))
                        else:
                            file_urls.extend(list(os.path.join(directory, f) for f in os.listdir(directory) if not os.path.isdir(
                                os.path.join(directory, f))))
                except (IOError, Exception) as e:
                    print(f'An error occurred in file_url_list_generator: {e}')
             # return file_urls
            for f in file_urls:
                if containing_str:  # if containing_str set, filenames not containing that substring are ignored
                    if containing_str in f:
                        yield f
                else:
                    yield f
        return False

    @staticmethod
    def read_iptc_tags(filename, path):
        """
        method to read IPTC tags
        :param filename: filename of image
        :param path: path to image
        :return: [{'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}] | False
        """
        try:
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            iptc_keys = meta.iptc_keys or []
            image_data = []
            if iptc_keys:
                for key in iptc_keys:
                    tag = meta[key]
                    image_data.append(
                        {'iptc_key': key, 'tags': tag.raw_value or []})
            # else:
            #     image_data.append({'iptc_key': '', 'tags': []})
            return image_data
        except (IOError, Exception) as e:
            print(f'An error occurred in read_iptc_tags: {e}')
            return False

    @staticmethod
    def write_iptc_tags(new_file_url: str, tag_data: dict) -> bool:
        """
        method to write IPTC tags to image
        :param new_file_url: filename of target image
        :param tag_data: image data: in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}
        :return: True | False
        """
        try:
            iptc_key = tag_data['iptc_key']
            if iptc_key:
                tags = tag_data['tags']
                meta = pyexiv2.ImageMetadata(new_file_url)
                meta.read()
                meta[iptc_key] = pyexiv2.IptcTag(iptc_key, tags)
                meta.write()
                print('Tags successfully written!')
                return True
            print('No tag to write!')
        except (TypeError, Exception) as e:
            print(f'An error occurred in write_iptc_tags: {e}')
        return False

    @staticmethod
    def convert_image(orig_filename, path, save_path, conversion_format):
        """
        method to convert the format and resize an image file
        :param orig_filename: original filename of image
        :param path: path of image
        :param conversion_format: file format to covert to
        :param save_path: where to save the converted image
        :return: {'orig_file_path': path, 'processed_path': save_path, 'new_filename': outfile,
        'orig_filename': orig_filename} | False
        Note: filename of converted file is a hexdigest sha1 hash of the original image file
        (the actual file - not the filename). This is to ensure unique files from different
        origin directories - but sharing the same filename - can be stored in processed
        directory without overwriting each other.
        """
        try:
            url = os.path.join(path, orig_filename)
            with Image.open(url) as img:
                # convert to conversion_format
                img.convert('RGB')  # convert to RGBA to ensure consistency
                new_filename = ProcessImages.generate_image_hash(
                    image_url=url)  # generate unique hash for image
                # define new filename (inc. extension for new format)
                outfile = f'{new_filename}.{conversion_format}'
                try:
                    img.save(os.path.normpath(
                        os.path.join(save_path, outfile)))
                except Exception as e:
                    img = img.point(lambda i: i*(1./256)).convert('L')
                    img.save(os.path.normpath(
                        os.path.join(save_path, outfile)))
                # create thumbs
                thumb_sizes = [(1080, 1080), (720, 720),
                               (350, 350), (150, 150), (75, 75)]
                for tn in thumb_sizes:
                    thumb_save_url = os.path.normpath(
                        f'{save_path}/tn/{new_filename}-{"_".join((str(t) for t in tn))}.{conversion_format}')
                    img.thumbnail(tn, resample=Image.BICUBIC)
                    img.save(thumb_save_url, quality=100)
                print('Conversion done!')
                return {'orig_path': path, 'processed_path': save_path, 'new_filename': outfile,
                        'orig_filename': orig_filename}
        except (IOError, Exception) as e:
            print(f'An error occurred in convert_format: {e}')
        return False

    @staticmethod
    def generate_image_hash(image_url=None):
        """
        method that generates a hexdigest sha1 hash of an image,
        either from an already open image object, or by opening
        an image at the image_url argument.
        :param image_url: url to image file
        :return: hexdigest of sha1 of hash of image file | None
        Note: hashing entire file (inc. meta), not just image data,
        as a) quicker and b) allows for duplicate images with different
        meta to be treated as separate files, which I decided is a
        required behaviour.
        """
        if image_url:
            with open(image_url, 'rb') as img:
                return hashlib.sha1(img.read()).hexdigest()
        return None

    @staticmethod
    def find_orphaned_images(origin_directories: list, processed_directory: str) -> list:
        """function to identify images existing in processed_directory
        which are not copies of an identical image in origin directories.
        :param origin_directories: list of full paths to dirs containing origin files
        :param processed_directory: url (str) of dir containing processed images to be scanned
        :return: list of urls of orphaned image files in processed_directory
        """

        # TODO ^^^ write this function
        print(f'Origin directories: {origin_directories}')
        print(f'Processed directory: {processed_directory}')
        return True

    @staticmethod
    def delete_images(allowed_dirs: set, allowed_formats: list, recursive: bool = False,
                      containing_str: str = '') -> bool:
        """function to delete images with filenames containing the filename hash
        within processed dir & sub dirs (thumbnails)
        :return: True | False
        """
        try:
            files_to_delete = ProcessImages.file_url_list_generator(directories=allowed_dirs, allowed_formats=allowed_formats,
                                                                    recursive=recursive, containing_str=containing_str)
            for f in files_to_delete:
                os.remove(f)
            return True
        except Exception as e:
            print(f'Error deleting the files: {e}')
        return False

    @staticmethod
    def add_tags(origin_file_url: str, tags: dict, retain_original: bool = True) -> bool:
        """
        method that  adds IPTC tags to an origin file, retaining existing tags
        :param origin_file_url: url of the file to which to add tags
        :param tags: tags to add to the file, in form e.g.:
            {'iptc_key': 'Iptc.Application2.Keywords', 'tags': ['new tag 1', 'new tag 2']}
        :param retain_original: bool: whether to retain original tags or simply replace with new
        :return: True|False
        """
        try:
            # get existing tags, if any, Expects: [{'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}] | False
            origin_filename = os.path.split(origin_file_url)[1]
            path = os.path.split(origin_file_url)[0]
            tags_to_write = []
            # merge existing & new tags to one list if retain_original is true
            if retain_original:
                tags_to_write = ProcessImages.read_iptc_tags(
                    filename=origin_filename, path=path)
                if tags_to_write:
                    for existing_tag in tags_to_write:
                        if existing_tag['iptc_key'] == tags['iptc_key']:
                            existing_tag['tags'] = existing_tag['tags'] + \
                                tags['tags']
            # if not merging with original or there were no original tags to merge, just use new
            tags_to_write = [tags] if not tags_to_write else tags_to_write
            # write tags to images (tags in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']})
            for tag in tags_to_write:
                ProcessImages.write_iptc_tags(
                    new_file_url=origin_file_url, tag_data=tag)
            return True
        except Exception as e:
            print(f'An exception occurred whilst attempting to add tags : {e}')
            return False

    def process_images(self):
        """
        generator method to run the image conversion and tagging processes
        :yield: generator, that processes files in an origin directory &
        produces dicts of saved conversion data and tags: e.g.:
            {conversion_data: {'orig_path': '/path/to/orig/image', 'processed_path':'/path/to/processed_image',
            'filename': '4058.jpeg'}, tag_data: {'iptc_key': 'Iptc.Application2.Keywords', 'tags':
            ['DATE: 1974', 'PLACE: The Moon']}
        Notes:
            1. Hash of origin file assigned as file name to ensure duplicate name of files in other
        origin directories do not overwrite pre-existing files of the same name in the processed directory.
            2. Only handle KEYWORDS IPTC key (TODO: for now! Implement others later)
            3. Yields {} if no successful outcome for any of the images
        """
        try:
            if self.process_single and self.origin_file_url:  # if a single image
                file_urls = [self.origin_file_url]
            else:  # if scanning directories
                file_urls = self.file_url_list_generator(
                    directories=self.ORIGIN_IMAGE_PATHS,
                    allowed_formats=self.ALLOWED_IMAGE_FORMATS,
                    recursive=True)
            for file_url in file_urls:
                try:
                    """
                    save converted file
                    """
                    # check if converted file already exists (need to check every file added, to prevent dupes)
                    original_img_hash = self.generate_image_hash(
                        image_url=file_url)
                    new_file_url = os.path.join(
                        self.PROCESSED_IMAGE_PATH, f'{original_img_hash}.{self.CONVERSION_FORMAT}')
                    converted_did_exist = new_file_url in [f for f in self.file_url_list_generator(
                        directories={self.PROCESSED_IMAGE_PATH})]
                    processed_data = {
                        'conversion_data': {
                            'orig_path': os.path.split(file_url)[0],
                            'orig_filename': os.path.split(file_url)[1],
                            'processed_path': self.PROCESSED_IMAGE_PATH,
                            'new_filename': os.path.split(new_file_url)[1]
                        },
                        'tag_data': {
                            'iptc_key': '', 'tags': []
                        }}
                    print(
                        f'Already exists in processed directory? : {converted_did_exist}')
                    # if filename does not already exist (not already converted)
                    if not converted_did_exist:
                        # save copy of the image with converted format & generate thumbs
                        self.convert_image(orig_filename=processed_data['conversion_data']['orig_filename'],
                                           path=processed_data['conversion_data']['orig_path'],
                                           save_path=processed_data['conversion_data']['processed_path'],
                                           conversion_format=self.CONVERSION_FORMAT)
                    """
                    write tags to file
                    """
                    if self.retag or not converted_did_exist:  # if retag is set, or newly converted image
                        # read tag data from original image
                        tag_data = self.read_iptc_tags(filename=processed_data['conversion_data']['orig_filename'],
                                                       path=processed_data['conversion_data']['orig_path'])
                        # any additions or updates to the incoming tag data
                        if tag_data:
                            # only handle IPTC keywords (for now)
                            for tag in tag_data:
                                if tag['iptc_key'] == 'Iptc.Application2.Keywords':
                                    tag['tags'].append(
                                        'SPM: TAGS COPIED FROM ORIGINAL')  # add tag to identify as copied
                                    # add to the return dicts
                                    processed_data['tag_data'] = tag
                                    # write the tags to the converted file
                                    self.write_iptc_tags(
                                        new_file_url=new_file_url, tag_data=tag)
                                else:
                                    print(
                                        f'No tag was saved for this file: {new_file_url}')
                        yield processed_data
                except Exception as e:
                    print(f'An error occurred whilst processing the file: {e}')
        except (TypeError, Exception) as e:
            print(f'Error occurred processing images, in main(): {e}')
            yield {}


if __name__ == '__main__':
    ProcessImages(origin_image_paths=ORIGIN_IMAGE_PATHS,
                  processed_image_path=PROCESSED_IMAGE_PATH,
                  origin_file_url=None,
                  thumb_path=THUMB_PATH,
                  conversion_format=CONVERSION_FORMAT,
                  process_single=False,
                  retag=False).process_images()
