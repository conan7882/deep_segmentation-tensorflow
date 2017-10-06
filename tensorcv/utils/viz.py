import matplotlib.pyplot as plt
import numpy as np
import scipy.misc

# copy from https://github.com/ppwwyyxx/tensorpack/blob/master/tensorpack/utils/viz.py
def intensity_to_rgb(intensity, cmap='cubehelix', normalize=False):
    """
    Convert a 1-channel matrix of intensities to an RGB image employing a colormap.
    This function requires matplotlib. See `matplotlib colormaps
    <http://matplotlib.org/examples/color/colormaps_reference.html>`_ for a
    list of available colormap.
    Args:
        intensity (np.ndarray): array of intensities such as saliency.
        cmap (str): name of the colormap to use.
        normalize (bool): if True, will normalize the intensity so that it has
            minimum 0 and maximum 1.
    Returns:
        np.ndarray: an RGB float32 image in range [0, 255], a colored heatmap.
    """
    assert intensity.ndim == 2, intensity.shape
    intensity = intensity.astype("float")

    if normalize:
        intensity -= intensity.min()
        intensity /= intensity.max()

    cmap = plt.get_cmap(cmap)
    intensity = cmap(intensity)[..., :3]
    return intensity.astype('float32') * 255.0

def save_merge_images(images, im_size, save_path, color = False, tanh = False):
    
    """
    Save the samples images
    The best size number is
            int(max(sqrt(image.shape[0]),sqrt(image.shape[1]))) + 1
    example:
        The batch_size is 64, then the size is recommended [8, 8]
        The batch_size is 32, then the size is recommended [6, 6]
    """

    # normalization of tanh output
    img = images
    if tanh:
        img = (img + 1.0) / 2.0

    if color:
    	# TODO
        img = intensity_to_rgb(np.squeeze(img), cmap='cubehelix', normalize=True)
        img = np.expand_dims(img, 0)

    if len(img.shape) == 2:
        img = np.expand_dims(img, 0)
    # img = images
    h, w = img.shape[1], img.shape[2]
    merge_img = np.zeros((h * im_size[0], w * im_size[1], 3))
    if len(img.shape) < 4:
        img = np.expand_dims(img, -1)

    for idx, image in enumerate(img):
        i = idx % im_size[1]
        j = idx // im_size[1]
        merge_img[j*h:j*h+h, i*w:i*w+w, :] = image
    
    return scipy.misc.imsave(save_path, merge_img)