#!/usr/bin/env python3
import glob
import os
import pyexiv2
from PIL import Image
import hashlib
from pathlib import Path
import glob

ORIGINAL_IMAGE_PATHS = set(os.path.normpath(os.path.normpath(
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

    def __init__(self, image_paths=None, processed_image_path=None, thumb_path=None, conversion_format=None,
                 retag=False):
        """
        initiate the class
        :param image_paths: set of paths of dirs of photos to be converted and/or tagged
        :param processed_image_path: path to save the processed image to
        :param conversion_format: file format to convert image to
        :param retag: boolean value, signifying whether to perform re-tagging
            if the image name already exists in the defined location where
            converted images are saved.
        Note: standardise on lowercase file extensions
        """
        self.ORIGINAL_IMAGE_PATHS = image_paths
        self.PROCESSED_IMAGE_PATH = processed_image_path
        self.THUMB_PATH = thumb_path
        self.CONVERSION_FORMAT = conversion_format.lower() \
            if conversion_format.lower() in self.ALLOWED_IMAGE_FORMATS else 'jpg'
        self.retag = retag if isinstance(retag, bool) else False

    @staticmethod
    def get_file_urls(directories, allowed_formats=None, recursive=False):
        """
        method to get full urls of all files in directories
        :param recursive: whether to scan recursively
        :param directories: list of directories in which to scan for files
        :return: a list of file urls
        """
        file_urls = []
        for index, directory in enumerate(directories):
            # for filename in os.listdir(image_path):
            try:
                if recursive:
                    if allowed_formats:
                        # produce <generator object>
                        url_list_generator = (Path(directory).glob(
                            f'**/*.{f}') for f in allowed_formats)
                        # produce [[], [PosixPath('/path/to/file.jpg')], []]
                        url_list = [list(x_file_type)
                                    for x_file_type in url_list_generator]
                        #produce ['/path/to/file.jpg', '/path2/to/file_2.jpg']
                        for urls_inner_list in url_list:
                            file_urls.extend([str(u) for u in urls_inner_list])
                    else:
                        item_list = (list(Path(directory).glob(f'**/*')))
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
                print(f'An error occurred in get_file_urls: {e}')
        return file_urls

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
            iptc_keys = meta.iptc_keys
            image_data = []
            if iptc_keys:
                for key in iptc_keys:
                    tag = meta[key]
                    image_data.append(
                        {'iptc_key': key, 'tags': tag.raw_value or []})
                print(image_data)
            else:
                image_data.append({'iptc_key': '', 'tags': []})
            return image_data
        except (IOError, Exception) as e:
            print(f'An error occurred in read_iptc_tags: {e}')
            return False

    @staticmethod
    def write_iptc_tags(new_file_url, tag_data):
        """
        method to write IPTC tags to image
        :param new_file_url: filename of target image
        :param tag_data: original image data: in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}
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
                #img.convert('RGB')  # convert to RGBA to ensure consistency
                new_filename = ProcessImages.generate_image_hash(
                    image_url=url)  # generate unique hash for image
                # define new filename (inc. extension for new format)
                outfile = f'{new_filename}.{conversion_format}'
                img.save(os.path.normpath(os.path.join(save_path, outfile)))
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

    def generate_processed_copies(self):
        """
        generator method to run the image conversion and tagging processes
        :yield: generator, that processes files in an origin directory &
        produces dicts of saved conversion data and tags: e.g.:
            {conversion_data: {'orig_path': '/path/to/orig/image', 'processed_path':'/path/to/processed_image',
            'filename': '4058.jpeg'}, tag_data: {'iptc_key': 'Iptc.Application2.Keywords', 'tags':
            ['DATE: 1974', 'PLACE: The Moon']}
        Notes:
            1. Hash of path appended to file names to ensure duplicate name of files in other
        origin directories do not overwrite pre-existing files of the same name in the processed directory.
            2. Only handle KEYWORDS IPTC key (TODO: for now! Implement others later - may require some debug)
        """
        try:
            file_urls = self.get_file_urls(
                directories=self.ORIGINAL_IMAGE_PATHS, allowed_formats=self.ALLOWED_IMAGE_FORMATS, recursive=True)
            for file_url in file_urls:
                """
                save converted file
                """
                # check if converted file already exists (need to check every file added, to prevent dupes)
                original_img_hash = self.generate_image_hash(
                    image_url=file_url)
                new_file_url = os.path.join(
                    self.PROCESSED_IMAGE_PATH, f'{original_img_hash}.{self.CONVERSION_FORMAT}')
                converted_did_exist = new_file_url in self.get_file_urls(
                    directories=[self.PROCESSED_IMAGE_PATH])
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
                print(f'New filename: {new_file_url}')
                # if filename does not already exist (not already converted)
                if not converted_did_exist:
                    # save copy of the image with converted format & generate thumbs
                    converted = self.convert_image(orig_filename=processed_data['conversion_data']['orig_filename'],
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
                        print(f'PROCESSED DATA: {processed_data}')
                    yield processed_data
        except (TypeError, Exception) as e:
            print(f'Error occurred processing images, in main(): {e}')
        return False


if __name__ == '__main__':
    ProcessImages(image_paths=ORIGINAL_IMAGE_PATHS,
                  processed_image_path=PROCESSED_IMAGE_PATH,
                  thumb_path=THUMB_PATH,
                  conversion_format=CONVERSION_FORMAT,
                  retag=False).generate_processed_copies()
