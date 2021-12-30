import os
import zipfile

import SimpleITK

from lib import img_lib

def get_available_gpus():
    from tensorflow.python.client import device_lib
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU' or x.device_type == 'XLA_GPU']

def get_available_cpus():
    """ Get available GPU devices info. """
    from tensorflow.python.client import device_lib
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'CPU' or x.device_type == 'XLA_CPU']

def zip_dir(src_dir, output_file_path):
    with zipfile.ZipFile(output_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(src_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, src_dir)
                zipf.write(file_path, rel_path)

def unzip_to_dir(src_file, output_dir):
    with zipfile.ZipFile(src_file, 'r') as zipr:
        zipr.extractall(output_dir)

def write_3d_image_as_slices(image, output_dir, file_prefix='image-', file_suffix='.png', image_io='PNGImageIO'):
    writer = SimpleITK.ImageFileWriter()
    writer.SetImageIO(image_io)

    image = img_lib.cast_to_unsigned(image)
    depth = image.GetDepth()
    extractor = SimpleITK.ExtractImageFilter()
    size = [
            image.GetWidth(),
            image.GetHeight(),
            0]
    extractor.SetSize(size)

    for i in range(depth):
        extractor.SetIndex([0, 0, i])
        image_slice = extractor.Execute(image)

        # eg. image-001.png
        file_name = file_prefix + ('%03d' % i) + file_suffix
        img_path = os.path.join(output_dir, file_name)
        writer.SetFileName(img_path)
        writer.Execute(image_slice)
