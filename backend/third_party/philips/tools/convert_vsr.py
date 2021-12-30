"""Simple tool to convert Philips ISD VSR images to DICOM."""

import argparse

import SimpleITK

import vsr_image

def main():
    parser = argparse.ArgumentParser(
            description="Simple tool to convert VSR iimages to DICOM.")
    parser.add_argument(
            'input_file',
            metavar='INPUT_FILE',
            help='(required) VSR image to convert.')
    parser.add_argument(
            'output_file',
            metavar='OUTPUT_FILE',
            help='(required) DICOM file to write.')

    args = parser.parse_args()

    image = vsr_image.VsrImage(args.input_file)

    sitk_image = image.sitkImage()

    if image.data.dtype == 'float32':
        cast_filter = SimpleITK.CastImageFilter()
        cast_filter.SetOutputPixelType(SimpleITK.sitkUInt16)
        sitk_image = cast_filter.Execute(sitk_image)
    else:
        print(
                "Warning: image.data.dtype not float32 (got: {}), but "
                "converting to sitkUInt16 anyways.".format(image.data.dtype))
        cast_filter = SimpleITK.CastImageFilter()
        cast_filter.SetOutputPixelType(SimpleITK.sitkUInt16)
        sitk_image = cast_filter.Execute(sitk_image)

    writer = SimpleITK.ImageFileWriter()
    writer.SetImageIO('GDCMImageIO')
    writer.SetFileName(args.output_file)
    writer.Execute(sitk_image)


if __name__ == '__main__':
    main()
