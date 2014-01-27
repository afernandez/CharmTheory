__author__ = 'Alejandro'

# Python Imports
import os
import hashlib

# Local Imports

# Third Party Imports
from PIL import Image

def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_file_size_bytes(file_path):
    size = 0
    with open(file_path, 'rb') as f:
        f.seek(0, 2)    # Move the cursor to the end of the file
        size = f.tell()
    return size


def scale_img_and_save(img, new_width, new_height, name, size_suffix, root_path, crop=True):
    """
    @param img: PIL image
    @param new_width: New width in pixels
    @param new_height: New height in pixels
    @param name: File name, e.g., foo.jpg
    @param size_suffix: Image size suffix like xs, s, m, l
    @param root_path: Root path of where to save the new image to, e.g., <root_path>\foo_xs.jpg
    @returns: Return the resized image
    """
    width, height = img.size
    print("Width: %d, Height: %d" % (width, height))

    width_ratio = width / new_width
    height_ratio = height / new_height
    print("Width ratio: %.4f, Height ratio: %.4f" % (width_ratio, height_ratio))
    ratio = min(width_ratio, height_ratio)  # Will crop after scaling

    scaled_width = int(width / ratio)
    scaled_height = int(height / ratio)
    print("Scaled width: %d, Scaled height: %d" % (scaled_width, scaled_height))

    crop_width = crop_height = 0
    if crop:
        crop_width = int((scaled_width - new_width) / 2.0)
        crop_height = int((scaled_height - new_height) / 2.0)
        print("Crop width: %d, Crop height: %d" % (crop_width, crop_height))

    resized_img = img.resize((scaled_width, scaled_height), Image.ANTIALIAS)
    print("Resized")

    resized_img = resized_img.crop((crop_width, crop_height, scaled_width - crop_width, scaled_height - crop_height))
    print("Cropped")

    name_and_ext = os.path.splitext(name)
    new_name_with_ext = name_and_ext[0] + "_" + size_suffix + name_and_ext[1]
    file_path = os.path.join(root_path, new_name_with_ext)
    resized_img.save(file_path, quality=100)
    print("Saved")
    return resized_img


def delete_files_with_suffix(filepath, suffixes):
    """
    @param filepath: File path to primary file
    @param suffixes: List of suffixes like xs, s, m, l
    @returns: Returns true if at least one file was deleted.
    """
    deleted = False
    head, tail = os.path.split(filepath)
    name_and_ext = os.path.splitext(tail)

    if suffixes and len(suffixes) > 0:
        for suffix in suffixes:
            path = os.path.join(head, name_and_ext[0] + "_" + suffix + name_and_ext[1])
            print("May delete path: %s" % str(path))
            if os.path.isfile(path):
                os.remove(path)
                deleted = True
    return deleted