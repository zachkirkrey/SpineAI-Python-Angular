"""Interface and utils for all UNet models."""

from config2.config import config
import tensorflow
from tensorflow import keras
from tensorflow.keras.layers import (
        Concatenate,
        Conv2D,
        Convolution2D,
        Conv2DTranspose,
        Dropout,
        Input,
        MaxPooling2D,
        UpSampling2D)
from tensorflow.compat.v1.keras.backend import set_session

import numpy
import SimpleITK
import skimage

tf_config = tensorflow.compat.v1.ConfigProto()
tf_config.gpu_options.allow_growth = True
tf_config.gpu_options.per_process_gpu_memory_fraction = config.spineai.classification.gpu.memory_fraction
tf_config.log_device_placement = True

sess = tensorflow.compat.v1.InteractiveSession(config=tf_config)
set_session(sess)

def get_canal_model(properties=None):
    keras.backend.set_image_data_format('channels_last')
    model_builder = BilwajModelBuilder()
    model_builder.set_property('residual', True)
    if properties is not None:
        for key in properties:
            model_builder.set_property(key, properties[key])
    return model_builder.build()


def get_disk_model(properties=None):
    keras.backend.set_image_data_format('channels_last')
    model_builder = BilwajModelBuilder()
    model_builder.set_property('residual', True)
    if properties is not None:
        for key in properties:
            model_builder.set_property(key, properties[key])
    return model_builder.build()


def get_foramen_model(properties=None):
    keras.backend.set_image_data_format('channels_last')
    model_builder = BilwajModelBuilder()
    if properties is not None:
        for key in properties:
            model_builder.set_property(key, properties[key])
    return model_builder.build()


def dice_coefficient(true, pred, smooth=0.1):
    """Dice coefficient loss function."""
    true_f = keras.backend.flatten(true)
    pred_f = keras.backend.flatten(pred)
    intersection = keras.backend.sum(true_f * pred_f)
    return ((2. * intersection + smooth) /
            (keras.backend.sum(true_f) +
             keras.backend.sum(pred_f) + smooth))


def dice_coefficient_loss(true, pred):
    return -1 * dice_coefficient(true, pred)


# TODO(billy): Rewrite and refactor this copied function.
def segment_patch(slice_,model,patchSize,disk=False):
    """Segments an image slice with the given model.

    Args:
        slice_: TODO(billy)
        model: TODO(billy)
        patchSize: TODO(billy)
        disk: (bool) If true, reshape the patch to conform with Theano model
            dimension expectations.
    """
    # TODO(billy): Clean up this code from bilwaj's code.

    # print slice_.shape
    step = int(patchSize/2)
    slice_ = skimage.util.pad(slice_,((step, step), (step, step)),'edge')
    # print slice_.shape
    seg = numpy.zeros_like(slice_)

    # slice_img = SimpleITK.GetImageFromArray(slice_)
    # SimpleITK.Show(slice_img)

    depth = 0
    for i in range(0,slice_.shape[0]+1-patchSize+step,step):
        for j in range(0,slice_.shape[1]+1-patchSize+step,step):

            patch = slice_[i:i+patchSize,j:j+patchSize]
            # patch_img = SimpleITK.GetImageFromArray(patch)
            # SimpleITK.Show(patch_img)
            # patch_img = img_lib.cast_to_unsigned(patch_img)
            # SimpleITK.WriteImage(
            #         patch_img,
            #         '/tmp/disk/' + str(i) + '_' + str(j) + '.png')
            if disk:
                patch = patch[numpy.newaxis,numpy.newaxis,...]
                if patch.shape[2]==patchSize and patch.shape[3]==patchSize:
                    patchSeg = model.predict(patch,verbose=1)
                    patch_seg_img = SimpleITK.GetImageFromArray(patchSeg[0,0,:,:])
                    # SimpleITK.Show(patch_seg_img)
                else:
                    patchSeg = numpy.zeros_like(patch)
                seg[i:i+patchSize,j:j+patchSize]=patchSeg[0,0,:,:,]
            else:
                patch = patch[numpy.newaxis,...,numpy.newaxis]
                if patch.shape[1]==patchSize and patch.shape[2]==patchSize:
                    patchSeg = model.predict(patch,verbose=1)
                else:
                    patchSeg = numpy.zeros_like(patch)
                seg[i:i+patchSize,j:j+patchSize]=patchSeg[0,:,:,0]

            depth += 1

    seg=seg[step:seg.shape[0]-step,step:seg.shape[1]-step]
    return seg


class BilwajModelBuilder(object):

    def __init__(self):
        pass

    @staticmethod
    def get_default_properties():
        """Returns default properties for a BilwajModel.

        Note that we assume all possible properties are enumerated here. If a
        new property is required, it should have a valid default added here.

        TODO(billy): Define property values.
        """
        return {
            'img_shape': (128, 128, 1),
            'out_ch': 1,
            'start_ch': 32,
            'depth': 5,
            'inc_rate': 2,
            'activation': 'relu',
            'dropout': 0.25,
            'batchnorm': False,
            'maxpool': True,
            'upconv': True,
            'residual': False,
            'metrics': [dice_coefficient],
            'loss_function': dice_coefficient_loss,
        }

    @property
    def properties(self):
        if not hasattr(self, '_properties'):
            self._properties = BilwajModelBuilder.get_default_properties()
        return self._properties

    @properties.setter
    def properties(self, unused_properties):
        raise AttributeError(
                'BilwajModelBuilder.properties should not be set directly.'
                ' See set_property() or set_properties()')

    def set_property(self, property_name, property_value):
        if property_name in self.properties:
            self._properties[property_name] = property_value
        else:
            raise KeyError(
                    'self._properties has no property %s' % property_name)

    def set_properties(self, new_properties):
        for property_name in new_properties:
            if property_name not in self.properties:
                raise KeyError(
                        'self._properties has no property %s' % property_name)
        self._properties = {**self._properties, **new_properties}

    def build(self):
        model_inputs = Input(shape=self.properties['img_shape'])

        # Build output tensors.
        # TOOD(billy): Refactor this into new UNet implementation.
        def conv_block(m, dim, acti, bn, res, do=0):
            n = Conv2D(dim, (3, 3), activation=acti, padding='same')(m)
            n = BatchNormalization()(n) if bn else n
            n = Dropout(do)(n) if do else n
            n = Conv2D(dim, (3, 3), activation=acti, padding='same')(n)
            n = BatchNormalization()(n) if bn else n
            return Concatenate()([m, n]) if res else n

        def level_block(m, dim, depth, inc, acti, do, bn, mp, up, res):
            if depth > 0:
                n = conv_block(m, dim, acti, bn, res)
                m = MaxPooling2D()(n) if mp else Conv2D(
                        dim, 3, strides=2, padding='same')(n)
                m = level_block(
                        m, int(inc*dim), depth-1, inc, acti, do, bn, mp, up,
                        res)
                if up:
                    m = UpSampling2D()(m)
                    m = Conv2D(
                            dim, (2, 2), activation=acti, padding='same')(m)
                else:
                    m = Conv2DTranspose(
                            dim, (3, 3), strides=2, activation=acti,
                            padding='same')(m)
                n = Concatenate()([n, m])
                m = conv_block(n, dim, acti, bn, res)
            else:
                m = conv_block(m, dim, acti, bn, res, do)
            return m

        model_outputs = level_block(
                model_inputs,
                self.properties['start_ch'],
                self.properties['depth'],
                self.properties['inc_rate'],
                self.properties['activation'],
                self.properties['dropout'],
                self.properties['batchnorm'],
                self.properties['maxpool'],
                self.properties['upconv'],
                self.properties['residual'])
        model_outputs = Conv2D(
                self.properties['out_ch'],
                (1, 1),
                activation='sigmoid')(model_outputs)

        model = keras.models.Model(inputs=model_inputs, outputs=model_outputs)
        model.compile(
                optimizer=keras.optimizers.Adam(lr=1e-5),
                loss=self.properties['loss_function'],
                metrics=self.properties['metrics'])

        return model
