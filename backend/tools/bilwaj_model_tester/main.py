"""Simple tool for testing models on sample images."""
import numpy

import SimpleITK

import classifier_lib
import img_lib
from lib import bilwaj_lib

PATCH_SIZE = 128

def segment_patch(
        model,
        weights_file_path,
        img_file_path,
        start_pos=(81,96),
        is_disk=False,
        show_patch=False):
    model.load_weights(weights_file_path)

    img = SimpleITK.ReadImage(img_file_path, SimpleITK.sitkFloat64)
    img_array = SimpleITK.GetArrayFromImage(img)

    start_pos = (81, 96)
    patch_arr = img_array[
            :,
            start_pos[0]:start_pos[0] + PATCH_SIZE,
            start_pos[1]:start_pos[1] + PATCH_SIZE]
    if is_disk:
        # Normalize all pixel valuees into [0, 1.0].
        # patch_arr = patch_arr / numpy.amax(patch_arr)

        # Rotate patch.
        # patch_arr[0] = numpy.rot90(patch_arr[0])

        # Flip patch vertically.
        # patch_arr[0] = numpy.flipud(patch_arr[0])

        pass
    if show_patch:
        patch_img = SimpleITK.GetImageFromArray(patch_arr)
        SimpleITK.Show(patch_img)

    if (is_disk):
        patch_arr = patch_arr[numpy.newaxis, ...]
    else:
        patch_arr = patch_arr[..., numpy.newaxis]

    return model.predict(patch_arr)


def main():
    # Segment foramen patch.
    # This works!
    # patch_arr = segment_patch(
    #      bilwaj_lib.get_foramen_model(),
    #      'bin/models/foramen/UNet.hdf5',
    #      'util/bilwaj_model_tester/img/sagittal-slice-05.dcm')

    # patch_img = SimpleITK.GetImageFromArray(patch_arr)
    # SimpleITK.Show(patch_img)

    # Segment disk patch.
    # This does not work. :
    patch_arr = segment_patch(
            bilwaj_lib.get_disk_model(),
            'bin/models/disk/UNet.hdf5',
            'util/bilwaj_model_tester/img/sagittal-slice-05.dcm',
            is_disk=True,
            show_patch=True)
    patch_arr = patch_arr[0, ...]

    patch_img = SimpleITK.GetImageFromArray(patch_arr)
    SimpleITK.Show(patch_img)


if __name__ == '__main__':
    main()
