"""Helper libraries for manipulating and processing images."""

import enum
import os

import cv2
import numpy
from PIL import Image
import scipy
import SimpleITK
import skimage

def normalize(image):
    """Normalize all values in image to [0, 1]."""
    img_array = SimpleITK.GetArrayFromImage(image)
    return SimpleITK.GetImageFromArray(normalize_arr(img_array))

def normalize_arr(image_array):
    max_value = image_array.flatten().max()
    return image_array/max_value

def n4_bias_field_correction(image):
    n4_filter = SimpleITK.N4BiasFieldCorrectionImageFilter()
    return n4_filter.Execute(image)

def histomatch(src_image, template_image):
    if src_image.GetPixelID() != template_image.GetPixelID():
        logging.warning(
                "histomatch: src_image pixel type does not match template. "
                "(got: {}, expected: {})".format(
                    src_image.GetPixelIDTypeAsString(),
                    template_image.GetPixelIDTypeAsString()))
    histomatch_filter = SimpleITK.HistogramMatchingImageFilter()
    histomatch_filter.SetNumberOfHistogramLevels(2048)
    histomatch_filter.SetNumberOfMatchPoints(100)
    histomatch_filter.ThresholdAtMeanIntensityOn()
    return histomatch_filter.Execute(src_image, template_image)

def invert(image):
    invert_filter = SimpleITK.InvertIntensityImageFilter()
    return invert_filter.Execute(image)

def min_area_filter(image, min_area):
    """
    Remove areas below a certain size.

    This function assumes pixel values > 0 are "on".

    Args:
        image (SimpleITK.Image): Image to process.
        min_area (int): The minimum area, in pixels, to keep.

    Returns:
        (SimpleITK.Image) an image with 0s for areas < min_area.
    """
    image_array = SimpleITK.GetArrayFromImage(image)
    num_dimensions = len(image_array.shape)
    if num_dimensions == 3:
        for i in range(image_array.shape[0]):
            min_area_filter_array(image_array[i], min_area)
        return SimpleITK.GetImageFromArray(image_array)
    elif num_dimensions == 2:
        min_area_filter_array(image_array, min_area)
        return SimpleITK.GetImageFromArray(image_array)
    else:
        raise TypeError(
                "image_array not 2 or 3-dimensional. got: %s" %
                str(image_array.shape))

def min_area_filter_array(image_array, min_area):
    if len(image_array.shape) != 2:
        raise TypeError(
                "image_array not 2-dimensional. got: %s" % image_array.shape)
    visited = numpy.zeros(image_array.shape)
    [x, y] = image_array.shape
    for i in range(x):
        for j in range(y):
            if not visited[i, j]:
                if image_array[i, j]:
                    area = set_area(image_array, (i, j), visited)
                    if area < min_area:
                        set_area(image_array, (i, j), new_value=0)
            visited[i, j] = 1

def traverse_area_helper(
        image_array, pos,
        start_row=None, end_row=None, start_col=None, end_col=None,
        visited=None,
        area_array=None):
    """
    Returns the boundaries of the area at the given position.

    Connected areas are defined as in set_area() below.

    Returns:
        (int, int, int, int, area_array) The (start_row, end_row, start_col,
        end_col) of the area at the given position, or (None, None, None, None)
        on invalid areas.
    """
    if area_array is None:
        area_array = numpy.zeros(image_array.shape)

    if visited is None:
        visited = numpy.zeros(image_array.shape)
    if visited[pos]:
        return (start_row, end_row, start_col, end_col, area_array)
    visited[pos] = 1

    if start_row is None:
        start_row = end_row = pos[0]
        start_col = end_col = pos[1]

    if image_array[pos]:
        area_array[pos] = 1.0
        (row, col) = pos
        if row < start_row:
            start_row = row
        if row > end_row:
            end_row = row
        if col < start_col:
            start_col = col
        if col > end_col:
            end_col = col
    else:
        return (start_row, end_row, start_col, end_col, area_array)

    neighbors = _get_valid_neighbors(image_array, pos)
    for neighbor in neighbors:
        (start_row, end_row, start_col, end_col, area_array) = traverse_area_helper(
                image_array, neighbor, start_row, end_row, start_col, end_col,
                visited, area_array)

    return (start_row, end_row, start_col, end_col, area_array)

# TODO(billy): Consider abstracting an Area object.
def get_area(image_array, position, visited=None):
    """
    Returns information about the given area.

    Connections are defined as in set_area() below.

    Returns:
        (dict) Information about the area, or None if there is no area at the
        given position.
    """
    if len(position) != 2:
        raise TypeError("position is not 2-dimensional. got: %s" % position)
    if len(image_array.shape) != 2:
        raise TypeError(
                "image_array not 2-dimensional. got: %s" % image_array.shape)

    if visited is not None and visited[position]:
        return None
    if not image_array[position]:
        return None

    area = {
        'size': None,
        'height': None,
        'width': None,
        'center': None,
        'sample_point': position,
    }
    area['size'] = set_area(image_array, position)

    (start_row, end_row, start_col, end_col, _) = traverse_area_helper(
            image_array, position, visited=visited)

    if None in (start_row, end_row, start_col, end_col):
        return None

    area['height'] = end_row - start_row + 1
    area['width'] = end_col - start_col + 1
    area['center'] = (
            (end_row + start_row) // 2,
            (end_col + start_col) // 2)

    return area


def set_area(image_array, position, visited=None, new_value=None):
    """
    Set the 2d connected area to a given value, if any.

    Connected areas are defined as pixels > 0, adjacent in position vertically
    or horizontally (but not diagonally unless otherwise connected).

    Returns:
        (int) the pixel size of area traversed.
    """
    if len(position) != 2:
        raise TypeError("position is not 2-dimensional. got: %s" % position)
    if len(image_array.shape) != 2:
        raise TypeError(
                "image_array not 2-dimensional. got: %s" % image_array.shape)
    
    if visited is None:
        visited = numpy.zeros(image_array.shape)

    (row, col) = position
    if visited[row, col]:
        return 0

    visited[row, col] = 1
    if not image_array[row, col]:
        return 0

    # Recursively get area of un-visited neighbors.
    area = 1
    neighbors = _get_valid_neighbors(image_array, position)
    for pos in neighbors:
        area += set_area(image_array, pos, visited, new_value)

    if not (new_value is None):
        image_array[row][col] = new_value

    return area

def max(*images):
    """Maximizes pixel values in images.

    Returns:
        (SimpleITK.Image) Image where each pixel value is the maximum value of
            the pixel values in the input images.
    """
    if not len(images):
        raise TypeError("max() called with no arguments")

    img_arrays = []
    for image in images:
        img_arrays.append(SimpleITK.GetArrayFromImage(image))

    new_array = max_array(*img_arrays)
    return SimpleITK.GetImageFromArray(new_array)

def max_array(*img_arrays):
    if not len(img_arrays):
        raise TypeError("max() called with no arguments")

    img_shape = None
    for img_array in img_arrays:
        if img_shape is None:
            img_shape = img_array.shape
        else:
            if img_shape != img_array.shape:
                raise TypeError(
                        'max_array() called with images with different '
                        'shapes. expected: %s, got: %s' %
                        (str(img_shape), str(img_array.shape)))

    new_array = numpy.zeros(img_shape)
    for img_array in img_arrays:
        new_array = numpy.maximum(new_array, img_array)
    return new_array

def _get_valid_neighbors(image_array, position):
    neighbors = []

    (row, col) = position
    (X, Y) = image_array.shape
    if row > 0:
        neighbors.append((row - 1, col))
    if row < X - 1:
        neighbors.append((row + 1, col))
    if col > 0:
        neighbors.append((row, col - 1))
    if col < Y - 1:
        neighbors.append((row, col + 1))

    return neighbors 

class Direction(enum.Enum):
    UP = 1
    DOWN = 2

def get_all_areas(image, scanning_direction=Direction.UP):
    image_array = SimpleITK.GetArrayFromImage(image)
    return get_all_areas_array(image_array, scanning_direction)

def get_all_areas_array(image_array, scanning_direction=Direction.UP):
    """Yields all the areas in a given image_array."""
    if len(image_array.shape) != 2:
        raise TypeError('expected 2-dimension image array. got: %s' % str(image_array.shape))

    (X, Y) = image_array.shape
    visited = numpy.zeros(image_array.shape)
    if scanning_direction == Direction.DOWN:
        for i in range(X):
            for j in range(Y):
                area = get_area(image_array, (i, j), visited)
                if area:
                    yield area
    elif scanning_direction == Direction.UP:
        for i in range(X - 1, -1, -1):
            for j in range(Y - 1, -1, -1):
                area = get_area(image_array, (i, j), visited)
                if area:
                    yield area

    else:
        raise TypeError(
                'scanning_direction not a valid Direction. got: %s' %
                str(scanning_direction))

def get_canal_row_px_from_disk_area(image_array, area):
    """Return the X position representing where to slice the canal.

    Current algorithm:
    - Get right 1/4 of area.
    - Find X position that slices that area by half, such that 50% of pixels
      are above and below that X position.

    TODO(billy): Possible better algorithm:
    - Get best-fit rectangle in 2D space for area.
    - Get slice at point halfway along right edge of rectangle.
    """
    (start_row, end_row, start_col, end_col, area_array) = traverse_area_helper(
            image_array, area['center'])

    col_threshold = int(end_col - (end_col - start_col) / 4)
    area_array[:, :col_threshold] = 0

    nonzero_positions = numpy.transpose(numpy.nonzero(area_array))
    x_sum = 0
    for x, y in nonzero_positions:
        x_sum += x

    if len(nonzero_positions):
        return int(round(x_sum / len(nonzero_positions)))
    else:
        return start_row

def cast_to_unsigned(image):
    array = SimpleITK.GetArrayFromImage(image)
    array = array * 65536 / numpy.amax(array)
    new_image = SimpleITK.GetImageFromArray(array)

    img_filter = SimpleITK.CastImageFilter()
    img_filter.SetOutputPixelType(SimpleITK.sitkUInt16)
    return img_filter.Execute(new_image)


def cast_to_unsigned_RGBA(image):
    img_filter = SimpleITK.CastImageFilter()
    img_filter.SetOutputPixelType(SimpleITK.sitkVectorUInt8)
    return img_filter.Execute(image)


def convert_mask_to_rgb(image, new_pixel_value=(255, 255, 255)):
    """Converts a greyscale SimpleITK image to an RGB one."""

    pixel_components = image.GetNumberOfComponentsPerPixel()
    if (pixel_components > 1):
        logging.error(
                'Cannot convert image to RGB. Pixels contain more than one '
                'component value. Got: {}'.format(pixel_components))
    image_arr = SimpleITK.GetArrayFromImage(image)

    image_rgb_arr = numpy.ndarray(
            shape = image_arr.shape + (3, ),
            dtype = numpy.uint8)
    image_rgb_arr[:] = (0)
    image_rgb_arr[image_arr > 0.0] = new_pixel_value

    image_rgb = SimpleITK.GetImageFromArray(image_rgb_arr)
    image_rgb.CopyInformation(image)

    return image_rgb

def array_slice_to_PIL(image_array, outline=False):
    def fill_contours(arr):
        return numpy.maximum.accumulate(arr, 1) &\
               numpy.maximum.accumulate(arr[:, ::-1], 1)[:, ::-1] &\
               numpy.maximum.accumulate(arr[::-1, :], 0)[::-1, :] &\
               numpy.maximum.accumulate(arr, 0)

    if outline:
        # Set values to 0 or 1.
        image_array[image_array > 0] = 1
        # Fill areas.
        image_array = fill_contours(image_array)

        # Get the border with binary erosion and XOR and set to 2.
        eroded = scipy.ndimage.morphology.binary_erosion(image_array).astype(image_array.dtype)
        border_array = image_array ^ eroded
        image_array = numpy.add(image_array, border_array)

    img = Image.fromarray(image_array)
    img_data = img.getdata()
    img = img.convert('RGBA')

    new_img_data = []
    for pixel in img_data:
        if pixel == 2:
            new_img_data.append((255, 255, 0, 255))
        elif pixel > 0:
            new_img_data.append((255, 0, 0, 50))
        else:
            new_img_data.append((255, 255, 255, 0))

    img.putdata(new_img_data)
    return img



def pretty_write_segmentation_img(image, file_path, filepattern='image-%03d.png'):
    """Writes 3D black/white segmentation images as semi-transparent PNG.

    If array is 2D, save image file as filepattern.
    If array is 3D, format filepattern with slice index.
    """
    image_array = SimpleITK.GetArrayFromImage(image)
    if len(image_array.shape) == 2:
        img = array_slice_to_PIL(image_array)
        img_path = os.path.join(file_path, filepattern)
        img.save(img_path)
    elif len(image_array.shape) == 3:
        for i, img_slice in enumerate(image_array):
            img = array_slice_to_PIL(img_slice)
            img_filename = filepattern % i
            img_slice_path = os.path.join(file_path, img_filename)
            img.save(img_slice_path)
    else:
        raise TypeError(
                "image_array not 2 or 3-dimensional. got: %s" % image_array.shape)


def resize(image, image_size, interpolation=cv2.INTER_NEAREST):
    """Resizes the given image to the given shape with opencv resize().

    Args:
        image: (SimpleITK.Image) 2d or 3d image to resize.
        image_size: (int, int) 2-d tuple of new image size (height, width).
            Note that this is the numpy/array convention, and not the SimpleITK
            GetSize() convention, which is (width, height, depth).
        interplation: cv2 interpolation type. See opencv InterpolationFlags.

    Returns:
        (SimpleITK.Image or None)
    """
    if len(image_size) != 2:
        logging.error('Expected 2d resize tuple. Got: {}'.format(image_size))
        return None

    # cv2 wants disred size as (width, height), which is opposite numpy and
    # SimpleITK. ¯\_(ツ)_/¯
    dsize = (image_size[1], image_size[0])

    image_array = SimpleITK.GetArrayFromImage(image)
    output_array = numpy.empty((0,) + image_size)
    for i, image_slice in enumerate(image_array):
        resized_slice = cv2.resize(image_slice, dsize=dsize, interpolation=interpolation)
        resized_slice = numpy.expand_dims(resized_slice, axis=0)
        output_array = numpy.append(output_array, resized_slice, axis=0)

    new_image = SimpleITK.GetImageFromArray(output_array)

    # TODO(billy): Fix origin.
    return new_image
