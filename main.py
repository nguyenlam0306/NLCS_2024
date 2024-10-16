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
import parser_config
import utils

class Grader:
# Tim khu vuc bai lam:
    def find_page(self, im):
        # Tim va tra ve o thong tin tra loi trong anh bai lam:
        """
              Tim va tra ve  test box với hình cho trước.

               Args:
                   im (numpy.ndarray): ảnh thử nghiệm.

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

    def scale_config_r(self, config, x_scale, y_scale, re_x, re_y):
        """
        Recursively scales lists within lists of values in the config dictionary
        based on the width and height of the image being graded.

        Args:
            config (dict): An unscaled coordinate mapping read from the
                configuration file.
            x_scale (int): Factor to scale x coordinates by.
            y_scale (int): Factor to scale y coordinates by.
            re_x (pattern): Regex pattern to match x coordinate key names.
            re_y (pattern): Regex pattern to match y coordinate key names.

        Returns:
            config (dict): A scaled coordinate mapping read from the
                configuration file.

        """
        for key, val in config.items():
            if isinstance(val, list):
                for config in val:
                    self.scale_config_r(config, x_scale, y_scale, re_x, re_y)
            if re_x.search(key) or key == 'bubble_width':
                config[key] = val * x_scale
            elif re_y.search(key) or key == 'bubble_height':
                config[key] = val * y_scale

    def scale_config(self, config, width, height):
        """
        Scales the values in the config dictionary based on the width and height
        of the image being graded.

        Args:
            config (dict): An unscaled coordinate mapping read from the
                configuration file.
            width (int): Width of the actual test image.
            height (int): Height of the actual test image.

        """
        x_scale = width / config['page_width']
        y_scale = height / config['page_height']

        # Regex to match strings like x, qr_x, and x_min.
        re_x = re.compile('(_|^)x(_|$)')
        re_y = re.compile('(_|^)y(_|$)')

        self.scale_config_r(config, x_scale, y_scale, re_x, re_y)

        # Ham grade quan trong:

    def grade(self, image_name, verbose_mode, debug_mode, scale):
        """
        Cham diem 1 test image aa tra ve ket qua ra man dang JSON object

        Args:
            image_name (str): Duong dan den test image de tien hanh cham diem.
            verbose_mode (bool): Che do verbose - chi tiet hoa, False
                otherwise.
            debug_mode (bool): Chay o che do debug, False
                otherwise.
            scale (str): Chinh ti le khung anh vua voi kich thuoc.

        """
        # Khoi tao tu dien tra ve:
        data = {
            'status' : 0,
            'error' : ''
        }

        # Cast str to float for scale.
        if scale is None:
            scale = 1.0
        else:
            try:
                scale = float(scale)
            except ValueError:
                data['status'] = 1
                data['error'] = f'Scale {scale} must be of type float'
                return json.dump(data, sys.stdout)

        # Verify that scale is positive.
        if scale <= 0:
            data['status'] = 1
            data['error'] = f'Scale {scale} must be positive'
            return json.dump(data, sys.stdout)

        # Kiem chung file phai la .png or .jpg
        if not (image_name.endswith('.png') or image_name.endswith('.jpg')):
            data['status'] = 1
            data['error'] = f'File {image_name} must be of type .png or .jpg'
            return json.dump(data, sys.stdout)

        # Khu vuc load hinh anh --> Camera:
        im = cv.imread(image_name)
        if im is None:
            data['status'] = 1
            data['error'] = f'Image {image_name} not found'
            return json.dump(data, sys.stdout);

        # Tim trang va tra ve ket qua
        page = self.find_page(im)
        if page is None:
            data['status'] = 1
            data['error'] = f'Page not found in {image_name}'
            return json.dump(data, sys.stdout);

        # Xac dinh khu vuc qr code:
        qr_code = self.decode_qr(page)
        if qr_code is None:
            data['status'] = 1
            data['error'] = f'QR code not found in {image_name}'
            return json.dump(data, sys.stdout);
        else:
            config_fname = qr_code.data.decode('utf-8')
            # Dua tren qrcode da doc xac dinh xem mau 6q hay mau 50q
            if '6q' in config_fname.lower():
                config_fname = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config/6ques.json')
            else:
                config_fname = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config/50ques.json')


        # Doc file config trong tu dien va gia tri cua ti le. Check duplicate xem key co trung khong
        # keys with object pairs hook.
        try:
            with open(config_fname) as file:
                config = json.load(file,
                    object_pairs_hook= parser_config.duplicate_key_check)
        except FileNotFoundError:
            data['status'] = 1
            data['error'] = f'Configuration file qrData not found'
            return json.dump(data, sys.stdout)


        # Tien hanh parse config theo config file va gia tri config nap vao:
        parser = parser_config.Parser(config, config_fname)
        status, error = parser.parse()
        if status == 1:
            data['status'] = 1
            data['error'] = error
            return json.dump(data, sys.stdout)




