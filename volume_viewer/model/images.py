import os
import re

import cv2
import numpy as np


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def resize_images(imgs, h, w, interpolation_flag=cv2.INTER_NEAREST, progress_function=None):
    """

    :param imgs: zxhxwxc
    :param h: New height
    :param w: New Width
    :return:
    """
    n = imgs.shape[0]
    c = imgs.shape[-1]
    out = np.empty((n, h, w, c), dtype=imgs.dtype)
    for i, img in enumerate(imgs):
        out[i] = cv2.resize(img, (w, h), interpolation=interpolation_flag)
        if progress_function is not None:
            progress_function(100 * i / n)
    return out


def read_images_to_np(folder, imread_flag=cv2.IMREAD_UNCHANGED, progress_function=None):
    """
    Expect the content of the folder to be composed of images (one or many)
    :return:
    """
    list_images_name = os.listdir(folder)
    n = len(list_images_name)
    if n > 1:
        list_images_name.sort(key=natural_keys)
        for i, img in enumerate(list_images_name):
            img = cv2.imread(os.path.join(folder, img), imread_flag)
            if img.ndim == 2:
                img = cv2.merge((img, img, img, np.ones_like(img) * 255))
            # img[:,:, 3] = 0
            if i == 0:
                imgs = np.empty((n,) + img.shape, dtype=img.dtype)
                imgs[0] = img
            imgs[i] = img

            if progress_function is not None:
                progress_function(100 * i / n)

        return np.moveaxis(imgs, 2, 1)
    else:
        img = cv2.imread(os.path.join(folder, list_images_name[0]), imread_flag)
        if img.ndim == 2:
            img = cv2.merge((img, img, img, img))
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

        img = np.expand_dims(img, 0)
        return img
