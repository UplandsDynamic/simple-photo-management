#!/usr/bin/env python3
import glob, os
import pyexiv2
from PIL import Image

ORIGINAL_IMAGE_PATH = os.path.normpath(os.path.normpath(os.path.join(os.getcwd(), '../test_images')))
PROCESSED_IMAGE_PATH = os.path.normpath(os.path.normpath(os.path.join(os.getcwd(), '../test_images/processed')))


class ProcessImages:
    """
    Processes images by:
        - convert image format (e.g. .tif to .jpg)
        - read & transfer IPTC 'keyword' tags from original to converted image
    """

    def __init__(self, image_path=None, processed_image_path=None):
        self.ORIGINAL_IMAGE_PATH = image_path
        self.PROCESSED_IMAGE_PATH = processed_image_path

    def read_iptc_tags(self, filename, path):
        """
        method to read IPTC tags
        :param filename: filename of image
        :param path: path to image
        :return: {'path': {'filename': ['a tag 1', 'a tag 2']}} | False
        """
        image_data = {path: dict()}
        try:
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            iptc_keys = meta.iptc_keys
            for key in iptc_keys:
                tag = meta[key]
                image_data[path][filename] = tag.raw_value
        except IOError as e:
            print(f'An error occurred: {e}')
            return False
        return image_data

    def write_iptc_tags(self, orig_filename, orig_path, converted_filename, converted_path):
        """
         method to copy IPTC tags from between images
        :param orig_filename: filename of image to copy from
        :param orig_path: path of image to copy from
        :param converted_filename: filename of image to copy to
        :param converted_path: path of image to copy to
        :return: True | False
        """
        # Read tags from original image
        orig_tags = self.read_iptc_tags(filename=orig_filename, path=orig_path)
        print(orig_tags)
        return False

    def convert_format(self, filename, path, save_directory):
        """
        method to convert the format of an image file
        :param filename: filename of image
        :param path: path of image
        :param save_directory: where to save the converted image
        :return: True | False
        """
        try:
            url = os.path.join(path, filename)
            file, extension = os.path.splitext(filename)
            outfile = f'{file}.jpg'
            Image.open(url).save(os.path.join(save_directory, outfile), quality=100)
            return True
        except (IOError, Exception) as e:
            print(f'An error occurred: {e}')
        return False

    def run(self):
        for filename in os.listdir(self.ORIGINAL_IMAGE_PATH):
            if not os.path.isdir(os.path.join(self.ORIGINAL_IMAGE_PATH, filename)):
                converted = self.convert_format(filename=filename, path=self.ORIGINAL_IMAGE_PATH,
                                                save_directory=self.PROCESSED_IMAGE_PATH)
                self.write_iptc_tags(orig_filename=filename, orig_path=self.ORIGINAL_IMAGE_PATH,
                                     converted_filename=filename, converted_path=self.PROCESSED_IMAGE_PATH)
                print('Resize done!' if converted else 'Resize failed!')


p = ProcessImages(image_path=ORIGINAL_IMAGE_PATH, processed_image_path=PROCESSED_IMAGE_PATH)
p.run()

# os.path.normpath('/mnt/adc_family_history/IMAGE_ARCHIVE/InProgress')
