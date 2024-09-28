import os
import sys
import argparse
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2 as cv
from imutils.perspective import four_point_transform
import pyzbar.pyzbar as pyzbar

import config
from test_box import TestBox
import utils

class Grader:
# Tim khu vuc bai lam:
    def define_page(self, im):
        # Tim va tra ve o thong tin tra loi trong anh bai lam:
        """
               Finds and returns the test box within a given image.

               Args:
                   im (numpy.ndarray): An ndarray representing the entire test image.

               Returns:
                   numpy.ndarray: An ndarray representing the test box in the image.

               """
        # Convert image to grayscale then blur to better detect contours.
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        threshold = utils.get_threshold(imgray)

        # Find contour for entire page.
        contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL,
                                      cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv.contourArea, reverse=True)

        if len(contours) > 0:
            # Approximate the contour.
            for contour in contours:
                peri = cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, 0.02 * peri, True)

                # Verify that contour has four corners.
                if len(approx) == 4:
                    page = approx
                    break
        else:
            return None
        return four_point_transform(imgray, page.reshape(4, 2))

# Nhận diện mã QR code

def decode_qr(self, im):
    """
    Finds and decodes the QR code inside of a test image.

    Args:
        im (numpy.ndarray): An ndarray representing the entire test image.

    Returns:
        pyzbar.Decoded: A decoded QR code object.

    """
    # Increase image contrast to better identify QR code.
    _, new_page = cv.threshold(im, 127, 255, cv.THRESH_BINARY)
    decoded_objects = pyzbar.decode(new_page)

    if not decoded_objects:
        return None
    else:
        return decoded_objects[0]

    def upright_image(self, page, config):
        """
        Rotates an image by 90 degree increments until it is upright.

        Args:
            page (numpy.ndarray): An ndarray representing the test image.
            config (dict): A dictionary containing the config file values.

        Returns:
            page (numpy.ndarray): An ndarray representing the upright test
                image.

        """
        if self.image_is_upright(page, config):
            return page
        else:
            for _ in range(3):
                page = utils.rotate_image(page, 90)
                if self.image_is_upright(page, config):
                    return page
        return None