import base64
import math
import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np


def get_threshold(im):
    """
    perform a guassian blur and threshold on a image for image processing.
    Returns the blurred and thresholded image.



    :param im:
    :return:
    """

    blurred = cv.GaussianBlur(im, (5,5), 0)
    _, threshold = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    return threshold


def get_transform(contour, im):
    peri = cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, 0.02*peri, True)

    return four_point_transform(im, approx.reshape(4,2))

def rotate_image(img, angle):
    """
        Xoay ảnh theo góc cho trước.
        """
    w = img.shape[1]
    h = img.shape[0]
    rads = np.deg2rad(angle)

    #Calculate new image width height.
    nw = abs(np.sin(rads) * h) + abs(np.cos(rads) * w)
    nh = abs(np.cos(rads) * h) + abs(np.sin(rads) * w)

    #Get the rotation matrix:
    rot_mat = cv.getRotationMatrix2D((nw * 0.5, nh*0.5), angle, 1)

    # Calculate the move from old center to new center combined with the
    # rotation.
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))

    # Update the translation of the transform.
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]

    return cv.warpAffine(img, rot_mat, (int(math.ceil(nw)),
                                       int(math.ceil(nh))), flags=cv.INTER_LANCZOS4)


def encode_image(image, format="png"):
    """
    Encodes an image into a base64 string.

    Args:
        image (numpy.ndarray): An ndarray representing an image.
        format (str): The format to encode the image in. Options are 'png' or 'jpg'.

    Returns:
        str: A base64 string encoding of the image, or None if the encoding fails.

    """
    if image is None:
        return None
    else:
        # Ensure the format is either 'png' or 'jpg'
        ext = '.jpg' if format.lower() in ['jpg', 'jpeg'] else '.png'

        # Encode the image to the required format
        success, binary = cv.imencode(ext, image)

        if success:
            # Convert binary data to base64
            encoded = base64.b64encode(binary)
            return encoded.decode('utf-8')
        else:
            return None