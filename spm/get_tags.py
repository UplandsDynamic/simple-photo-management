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
        :return: {'path': path, 'filename': filename, 'key': key, 'tags': ['tag 1', 'tag 2']} | False
        """
        try:
            image_data = {}
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            iptc_keys = meta.iptc_keys
            for key in iptc_keys:
                tag = meta[key]
                image_data = {'path': path, 'filename': filename, 'iptc_key': key, 'tags': tag.raw_value}
            return image_data
        except IOError as e:
            print(f'An error occurred: {e}')
            return False

    def write_iptc_tags(self, path, filename, tag_data):
        """
        method to write new IPTC tags to image
        :param path: path to image
        :param filename: filename of image
        :param tag_data: original image data: in form:
            {'path': path, 'filename': filename, 'iptc_key': key, 'tags': ['tag 1', 'tag 2']}
        :return: True | False
        """
        try:
            iptc_key = tag_data['iptc_key']
            tags = tag_data['tags']
            url = os.path.join(path, filename)
            meta = pyexiv2.ImageMetadata(os.path.join(url))
            meta.read()
            meta[iptc_key] = pyexiv2.IptcTag(iptc_key, tags)
            meta.write()
            print('Tags successfully written!')
            return True
        except (TypeError, Exception) as e:
            print(e)
        return False

    def convert_format(self, filename, path, save_path):
        """
        method to convert the format of an image file
        :param filename: filename of image
        :param path: path of image
        :param save_directory: where to save the converted image
        :return: [new file path, new file filename] | False
        """
        try:
            url = os.path.join(path, filename)
            file, extension = os.path.splitext(filename)
            outfile = f'{file}.jpg'
            Image.open(url).save(os.path.join(save_path, outfile), quality=100)
            print('Conversion done!')
            return {'path': save_path, 'filename': outfile}
        except (IOError, Exception) as e:
            print(f'An error occurred: {e}')
        return False

    def run(self):
        for filename in os.listdir(self.ORIGINAL_IMAGE_PATH):
            if not os.path.isdir(os.path.join(self.ORIGINAL_IMAGE_PATH, filename)):
                # save copy of the image with converted format
                converted = self.convert_format(filename=filename, path=self.ORIGINAL_IMAGE_PATH,
                                                save_path=self.PROCESSED_IMAGE_PATH)
                # read tag data from original image
                tag_data = self.read_iptc_tags(filename=filename, path=self.ORIGINAL_IMAGE_PATH)
                # write tag data to the converted copy
                self.write_iptc_tags(path=self.PROCESSED_IMAGE_PATH, filename=converted['filename'], tag_data=tag_data)


p = ProcessImages(image_path=ORIGINAL_IMAGE_PATH, processed_image_path=PROCESSED_IMAGE_PATH)
p.run()

# os.path.normpath('/mnt/adc_family_history/IMAGE_ARCHIVE/InProgress')
