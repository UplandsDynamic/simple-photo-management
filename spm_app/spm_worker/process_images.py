#!/usr/bin/env python3
import glob
import os
import pyexiv2
from PIL import Image
import hashlib
from pathlib import Path
import glob
import traceback
import logging
from typing import List

ORIGIN_IMAGE_PATHS = set(os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../photo_directory")}')))
PROCESSED_IMAGE_PATH = os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../media/photos")}'))
THUMB_PATH = os.path.normpath(os.path.normpath(
    f'{os.path.join(os.getcwd(), "../media/photos/tn")}'))
THUMB_SIZES = [(1080, 1080), (720, 720), (350, 350), (150, 150), (75, 75)]
CONVERSION_FORMAT = 'jpg'

# Get an instance of a logger
logger = logging.getLogger('django')

# remove limit on image size
Image.MAX_IMAGE_PIXELS = None

class ProcessImages:
    """
    Processes images by:
        - convert image format (e.g. .tif to .jpg)
        - read & transfer IPTC 'keyword' tags from original to converted image
    """
    ALLOWED_IMAGE_FORMATS = ['jpeg', 'jpg', 'tiff', 'tif', 'png']

    def __init__(
            self, origin_image_paths=None, origin_file_url=None, processed_image_path=None, thumb_path=None,
            conversion_format=None, retag=False, process_single=False, reprocess=False, thumb_sizes: List[tuple] = [],
            tags=None):
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
        :param thumb_sizes: [tuple]: list of thumb sizes, in form: [(75,75),(150,150)]. Default to 75,75
        Note: standardise on lowercase file extensions
        """
        self.ORIGIN_IMAGE_PATHS = origin_image_paths
        self.PROCESSED_IMAGE_PATH = processed_image_path
        self.THUMB_PATH = thumb_path
        self.THUMB_SIZES = thumb_sizes
        self.CONVERSION_FORMAT = conversion_format.lower() \
            if conversion_format.lower() in self.ALLOWED_IMAGE_FORMATS else None
        self.retag = retag if isinstance(retag, bool) else False
        self.process_single = process_single
        self.origin_file_url = origin_file_url
        self.reprocess = reprocess
        self.tags = tags

    @staticmethod
    def file_url_list_generator(directories: set, allowed_formats: list = ALLOWED_IMAGE_FORMATS, recursive: bool = False,
                                containing_str: str = '') -> str:
        """
        generator method, to get full urls of all files in directories
        :param recursive: whether to scan recursively
        :param directories: set of directories in which to scan for files
        :param containing_str: string that included filenames must contain (if any)
        :param allowed_formats: list: list of file extensions to restrict to (default as ALLOWED_IMAGE_FORMATS const)
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
                            # produce ['/path/to/file.jpg', '/path2/to/file_2.jpg']
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
                            file_urls.extend(list(os.path.join(directory, f) for f in os.listdir(
                                directory) if os.path.splitext(f)[1].strip('.') in allowed_formats))
                        else:
                            file_urls.extend(list(os.path.join(directory, f) for f in os.listdir(
                                directory) if not os.path.isdir(os.path.join(directory, f))))
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
    def _read_iptc_tags(filename, path):
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
        except (IOError, KeyError, Exception) as e:
            logger.error(f'Error in _read_iptc_tags: {e}')
            return False

    @staticmethod
    def _write_iptc_tags(new_file_url: str, tag_data: dict) -> bool:
        """
        method to write IPTC tags to image
        :param new_file_url: filename of target image
        :param tag_data: image data: in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}
        :return: True | False
        """
        try:
            iptc_key = tag_data['iptc_key']
            if iptc_key and tag_data['tags']:
                tags = tag_data['tags']
                logger.info(f'Tags to write: {tags}')
                meta = pyexiv2.ImageMetadata(new_file_url)
                meta.read()
                meta[iptc_key] = pyexiv2.IptcTag(iptc_key, tags)
                meta.write()
            else:
                logger.warning(
                    'NO TAGS WERE SUBMITTED TO WRITE, SO ASSUMING ONLY 1 TAG EXISTED & THE INTENTION WAS TO WRITE AN EMPTY TAG SET, WITH THE EFFECT OF DELETING IT')
                ProcessImages.delete_iptc_tags(new_file_url)  # delete the tag
            logger.info('No more tags to write!')
        except (TypeError, Exception) as e:
            logger.error(f'An error occurred in write_iptc_tags: {e}')
        return False

    @staticmethod
    def delete_iptc_tags(file_url: str, tag_type_to_delete: str = None) -> bool:
        """
        method to delete IPTC tags from image
        :param file_url: filename of target image
        :param tag_type_to_delete: IPTC tag type to delete
        :return: True | False
        """
        logger.info(f'DELETING TAGS FROM: {file_url}')
        try:
            meta = pyexiv2.ImageMetadata(file_url)
            meta.read()  # read the meta
            # delete specific tag type
            if tag_type_to_delete:
                try:
                    #del meta.iptc_keys[tag_type_to_delete]
                    meta.__delitem__(tag_type_to_delete)
                    logger.info(f'TAG TYPE {tag_type_to_delete} SUCCESSFULLY DELETED!')
                    meta.write() # save the meta
                    return True
                except (TypeError, Exception) as e:
                    logger.warning(f'DELETION ERROR: {e}')
                    logger.info(f'NO TAG OF TYPE {tag_type_to_delete} TO DELETE FROM IMAGE {file_url}!')
                    return False
            else:
                # delete all tags
                loop_count = 0
                while loop_count < 10:
                    for key in meta.iptc_keys:  # delete all keys
                        del meta[key]
                    meta.write()  # save the meta
                    loop_count += 1
                    # check all tags successfully cleared
                    meta = pyexiv2.ImageMetadata(file_url)
                    meta.read()
                    if not meta.iptc_keys:
                        break
                return loop_count < 10  # return True if successfully ended loop, else False
        except (TypeError, Exception) as e:
            print(f'An error occurred in delete_iptc_tags: {e}')

    @staticmethod
    def convert_image(orig_filename: str, path: str, save_path: str, conversion_format: str,
                      thumb_path: str = '', change_filename: bool = True, thumbs_only: bool = False,
                      thumb_sizes: List[tuple] = [(75, 75)]) -> dict or bool:
        """
        method to convert the format and resize an image file
        :param orig_filename: original filename of image
        :param path: path of origin image
        :param save_path: path to save the converstion to
        :param conversion_format: file format to covert to
        :param thumb_path: path to save the thumbnails to
        :param change_filename: bool: whether to generate a new filename, based on hash of origin file
        :param thumbs_only: bool: whether only to generate thumbs (not the full sized processed image)
        :param thumb_sizes: [tuple]: list of thumb sizes, in form: [(75,75),(150,150)]. Default to 75,75
        :return: {'orig_file_path': path, 'processed_path': save_path, 'new_filename': outfile,
        'orig_filename': orig_filename, 'thumb_path': thumb_path} | False
        Note: filename of converted file is a hexdigest sha1 hash of the original image file
        (the actual file - not the filename). This is to ensure unique files from different
        origin directories - but sharing the same filename - can be stored in processed
        directory without overwriting each other.
        """
        try:
            # Map arg to uppercase, jpg to JPEG, etc
            url = os.path.join(path, orig_filename)
            with Image.open(url) as img:
                # convert to conversion_format
                img.convert('RGB')  # convert to RGBA to ensure consistency
                if change_filename:
                    new_filename = ProcessImages.generate_image_hash(
                        image_url=url)  # generate unique hash for image if required
                else:
                    # get filename minus format extension
                    new_filename = os.path.splitext(orig_filename)[0]
                # define new filename (inc. extension for new format)
                outfile = f'{new_filename}.{conversion_format}'
                if not thumbs_only:  # if converting to a full-sized copy
                    try:
                        img.save(os.path.normpath(
                            os.path.join(save_path, outfile)))
                    except Exception as e:
                        img = img.point(lambda i: i*(1./256)).convert('L')
                        img.save(os.path.normpath(
                            os.path.join(save_path, outfile)))
                # create thumbs
                for tn in thumb_sizes:
                    if thumb_path:
                        thumb_save_url = os.path.join(
                            thumb_path, f'{new_filename}-{"_".join((str(t) for t in tn))}.{conversion_format}')
                    else:
                        thumb_save_url = os.path.join(
                            save_path, 'tn', f'{new_filename}-{"_".join((str(t) for t in tn))}.{conversion_format}')
                    img.thumbnail(tn, resample=Image.BICUBIC)
                    img.save(thumb_save_url, quality=100)
                logger.info('Conversion done!')
                return {'orig_path': path, 'processed_path': save_path, 'new_filename': outfile,
                        'orig_filename': orig_filename, 'thumb_path': thumb_path}
        except (IOError, Exception) as e:
            logger.error(f'An error occurred in convert_format: {e}')
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
            files_to_delete = ProcessImages.file_url_list_generator(
                directories=allowed_dirs, allowed_formats=allowed_formats, recursive=recursive,
                containing_str=containing_str)
            for f in files_to_delete:
                os.remove(f)
            return True
        except Exception as e:
            print(f'Error deleting the files: {e}')
        return False

    @staticmethod
    def add_tags(target_file_url: str, tags: dict, retain_original: bool = True) -> bool:
        """
        method that adds IPTC tags to a target file, retaining existing tags
        :param target_file_url: url of the file to which to add tags
        :param tags: tags to add to the file, in form e.g.:
            {'iptc_key': 'Iptc.Application2.Keywords',
                'tags': ['new tag 1', 'new tag 2']}
        :param retain_original: bool: whether to retain original tags or simply replace with new
        :return: True (if Excpetion not raised)
        """
        logger.info(
            f'ADDING TAGS: [target: {target_file_url}, tags: {tags}, retain_original: {retain_original}]')
        try:
            # get existing tags, if any, Expects: [{'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']}] | False
            path, target_filename = os.path.split(target_file_url)
            tags_to_write = []
            # merge existing & new tags to one list if retain_original is true
            if retain_original:
                tags_to_write = ProcessImages._read_iptc_tags(
                    filename=target_filename, path=path)
                logger.info(f'ORIGINAL TAGS TO COPY: {tags_to_write}')
                logger.info(f'COPIED FROM FILENAME: {target_filename}')
                logger.info(f'COPIED FROM PATH: {path}')
                if tags_to_write:
                    for existing_tag in tags_to_write:
                        if existing_tag['iptc_key'] == tags['iptc_key']:
                            existing_tag['tags'] = existing_tag['tags'] + \
                                tags['tags']
            # if not merging with original or there were no original tags to merge, just use new
            tags_to_write = [tags] if not tags_to_write else tags_to_write
            # write tags to images (tags in form: {'iptc_key': iptc key, 'tags': ['tag 1', 'tag 2']})
            logger.info(f'WRITING THESE TAGS: {tags_to_write}')
            for tag in tags_to_write:
                ProcessImages._write_iptc_tags(
                    new_file_url=target_file_url, tag_data=tag)
            # check successful write
            if not ProcessImages.tag_write_error_check(
                    intended_tags=tags, origin_image_path=path, origin_image_filename=target_filename):
                logger.error('TAGS NOT WRITTEN CORRECTLY!')
                return False
        except Exception as e:
            print(f'An exception occurred whilst attempting to add tags : {e}')
            raise
        return True

    @staticmethod
    def tag_write_error_check(
            intended_tags: dict = {},
            origin_image_path: str = '', origin_image_filename: str = '') -> bool:
        image_data = ProcessImages._read_iptc_tags(
            origin_image_filename, origin_image_path)
        logger.info(f'TAGS LOOKING FOR: {intended_tags}')
        if not image_data:
            logger.info('THERE WERE NO TAGS ON THE PROCESSED FILE')
        elif not intended_tags['tags']:
            # return True if no tags, as tags were deleted not written
            logger.info('TAGS WERE BEING DELETED AND WRITE WAS SUCCESSFUL!')
            return True
        else:
            key_found = False
            for t in intended_tags['tags']:
                for d in image_data:
                    if d['iptc_key'] == intended_tags['iptc_key']:
                        key_found = True
                        if t not in d['tags']:
                            logger.error(
                                'Error: The key WAS found - but the tag was NOT written!')
                            return False
            if intended_tags['tags'] and not key_found:
                logger.error('Error: The key was NOT found and the tag was NOT written!')
                return False
        return True

    @staticmethod
    def rename_image(url_file_to_hash: str = '', url_file_to_rename: str = '', with_hash: bool = False,
                     new_name: str = '') -> str:
        """function to rename a file
        :param url_file_to_hash: str: url of image file to be sha1 hashed (if any)
        :param url_file_to_rename: str: url of file to be renamed
        :param with_hash: bool: whether to rename with the sha1 hash of an image file
        :param new_name: str: filename to rename to (if with_hash not True)
        :return: str: new url of renamed file
        """
        try:
            path, old_filename = os.path.split(url_file_to_rename)
            if with_hash:
                hash = ProcessImages.generate_image_hash(
                    image_url=url_file_to_hash)
                new_url = os.path.join(
                    path, hash + os.path.splitext(old_filename)[1])
            else:
                new_url = os.path.join(path, new_name)
            print(f'NEW URL: {new_url}')
            os.rename(src=url_file_to_rename, dst=new_url)
            return new_url
        except Exception as e:
            print(
                f'An exception occurred whilst attempting to rename the files: {e}')
            raise

    @staticmethod
    def rotate_image(
            origin_file_url: str, rotation_degrees: int = 90, copy_tags: bool = True, recreate_thumbs: bool = True,
            save_path: str = '', save_format: str = '', thumb_path: str = '', thumb_sizes: List[tuple] = []) -> bool:
        """function to rotate an image
        :param origin_file_url: str: url of the image file to rotate
        :param copy_tags: bool: whether to copy IPTC tags from original to rotated image
        :param degrees: int: number of degrees to rotate the image
        :param thumb_sizes: [tuple]: list of thumb sizes, in form: thumb_sizes = [(1080, 1080), (720, 720)]
        :return: bool: True|False
        """
        try:
            tags = []
            path, filename = os.path.split(origin_file_url)
            if copy_tags:  # read tags
                tags = ProcessImages._read_iptc_tags(
                    filename=filename, path=path)
                print(f'original TAGS: {tags}')
            # rotate the image (makes a new copy & overwrites the origial)
            with Image.open(origin_file_url) as img:
                img.rotate(rotation_degrees, resample=Image.BICUBIC,
                           expand=True).save(origin_file_url)
            if copy_tags and tags:  # write tags to new copy
                for tag in tags:
                    ProcessImages.add_tags(
                        target_file_url=origin_file_url, tags=tag, retain_original=True)
            # convert to create thumbs
            if recreate_thumbs:
                ProcessImages.convert_image(
                    orig_filename=filename, path=path, save_path=save_path, thumb_path=thumb_path,
                    conversion_format=save_format, change_filename=False, thumbs_only=True, thumb_sizes=thumb_sizes)
            return True
        except IOError as e:
            print(f'Image rotation failed: {e}')
        return False

    def process_images(self):
        """
        generator method to run the image conversion and tagging processes
        :yield: generator, that processes files in an origin directory &
        produces dicts of saved conversion data and tags: e.g.:
            {conversion_data: {'orig_path': '/path/to/orig/image', 'processed_path':'/path/to/processed_image',
            'filename': 'jfJJeke5wrt54646ehgoe462.jpeg'}, tag_data: {'iptc_key': 'Iptc.Application2.Keywords', 'tags':
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
                    if self.reprocess:
                        print('Reprocessing existing record ...')
                    # if filename does not already exist (not already converted)
                    if not converted_did_exist or self.reprocess:
                        # save copy of the image with converted format & generate thumbs
                        self.convert_image(orig_filename=processed_data['conversion_data']['orig_filename'],
                                           path=processed_data['conversion_data']['orig_path'],
                                           save_path=processed_data['conversion_data']['processed_path'],
                                           conversion_format=self.CONVERSION_FORMAT,
                                           thumb_path=self.THUMB_PATH,
                                           thumb_sizes=self.THUMB_SIZES)
                    """
                    write tags to file if any of:
                      - retag is True
                      - it's a newly converted file
                      - reprocess is True
                    """
                    if self.retag or self.reprocess or not converted_did_exist:
                        # read tag data from original image
                        tag_data = self._read_iptc_tags(filename=processed_data['conversion_data']['orig_filename'],
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
                                    self._write_iptc_tags(
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
                  reprocess=False,
                  retag=False,
                  thumb_sizes=THUMB_SIZES).process_images()
