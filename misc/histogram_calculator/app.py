import glob
import sys

from matplotlib import pyplot
import numpy
import skimage.io
import skimage.viewer


def main():
    pyplot.figure()
    pyplot.title("Histogram")
    pyplot.xlabel('value')
    pyplot.ylabel('# pixels')
    pyplot.xlim([0.0, 1.0])

    filenames = glob.glob('/opt/spineai/files/UCLA_Training/canal/images_png/*/*.png')

    r = 0
    g = 0
    b = 0
    for filename in filenames[0:1000]:
        image = skimage.io.imread(fname=filename, as_gray=True)
        histogram, bin_edges = numpy.histogram(image, bins=64, range=(0,1))

        b += 1
        if b > 255:
            b = 0
            g += 1
            if g > 255:
                g = 255

        hex_color = '#%02x%02x%02x' % (r, g, b)

        pyplot.plot(bin_edges[0:-1], histogram, color=hex_color)

    pyplot.show()



if __name__ == "__main__":
    main()
