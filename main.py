import os
import sys
import argparse
import json
import re
import cv2 as cv
from imutils.perspective import four_point_transform
import pyzbar.pyzbar as pyzbar
import parser_config
import utils
from test_box import TestBox

class Grader:
# Tim khu vuc bai lam:
    def find_page(self, im):
        # Tim va tra ve o thong tin tra loi trong anh bai lam:
        """
              Tim va tra ve khu vưc bài làm với hình cho trước.

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
        Tìm và trả về QR code trong ảnh bài làm

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


    def image_is_upright(self, page, config):
        """
        Kiem tra xem anh co bi upright dưa tren toa do cua QR trong anh
        :param page:
        :param config:
        :return:
        True: Upright
        False: Otherwise
        """
        qr_code = self.decode_qr(page)
        qr_x = qr_code.rect.left
        qr_y = qr_code.rect.top
        x_error = config['x_error']
        y_error = config['y_error']

        if (config['qr_x'] - x_error <= qr_x <= config['qr_x'] + x_error) and (config['qr_y'] - y_error <= qr_y <= config['qr_y'] + y_error):
            return True
        else:
            return False


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


    def load_correct_answers(self, file_path):
        """
        Load đáp án đúng từ file JSON.

        Args:
            file_path (str): Đường dẫn tới file JSON chứa đáp án đúng.

        Returns:
            dict: Dictionary chứa đáp án đúng cho từng phiên bản.
        """
        try:
            with open(file_path, 'r') as f:
                correct_answers = json.load(f)
            return correct_answers
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
            return {}


    def calculate_score(self, data, version_correct_answers):
        """
        Tính điểm dựa trên câu trả lời của người dùng và đáp án đúng.

        Args:
            data (dict): Kết quả đọc từ các box chấm được.
            version_correct_answers (dict): Đáp án đúng cho từng phiên bản.

        Returns:
            dict: Dữ liệu cập nhật với điểm số.
        """
        # Lấy phiên bản từ kết quả
        selected_version = data.get("version", {}).get("bubbled", [])
        if not selected_version:
            data['status'] = 1
            data['error'] = "Khong xac dinh duoc phien ban"
            return data

        selected_version = selected_version[0]  # Giả sử chỉ có một phiên bản
        user_answers = data.get("answer", {}).get("bubbled", [])

        # Kiểm tra xem phiên bản có tồn tại trong đáp án đúng không
        if selected_version not in version_correct_answers:
            data['status'] = 1
            data['error'] = "Phien ban khong hop le hoac khong co dap an cho phien ban nay"
            return data

        # Lấy đáp án đúng dựa trên phiên bản
        correct_answers = version_correct_answers[selected_version]

        # Tính điểm
        score = sum(1 for user_ans, correct_ans in zip(user_answers, correct_answers) if user_ans == correct_ans)
        total_questions = len(correct_answers)

        # Cập nhật điểm vào data
        data['score'] = {
            'correct': score,
            'total': total_questions,
            'percentage': round((score / total_questions) * 100, 2)
        }

        return data

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
            # Đọc đáp án đúng từ file JSON
        correct_answers_file = 'config/correct_answer.json'
        version_correct_answers = self.load_correct_answers(correct_answers_file)
        print(version_correct_answers)
        if version_correct_answers is None:
            data['status'] = 1
            data['error'] = 'Could not load correct answers from file.'
            return json.dump(data, sys.stdout)


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

        # Scale config values based on page size.
        self.scale_config(config, page.shape[1], page.shape[0])

        # Rotate page until upright.
        page = self.upright_image(page, config)
        if page is None:
            data['status'] = 1
            data['error'] = f'Could not upright page in {image_name}'
            return json.dump(data, sys.stdout);

        # Grade each test box and add result to data.
        for box_config in config['boxes']:
            box_config['x_error'] = config['x_error']
            box_config['y_error'] = config['y_error']
            box_config['bubble_width'] = config['bubble_width']
            box_config['bubble_height'] = config['bubble_height']
            box = TestBox(page, box_config, verbose_mode, debug_mode, scale)
            data[box.name] = box.grade()

        #     # Đáp án đúng cho các phiên bản
        # version_correct_answers = {
        #     "A": ["A", "B", "C", "D", "A", "E"],
        #     "D": ["A", "B", "C", "D", "A", "E"],
        # }

        # Tính điểm và cập nhật vào data
        data = self.calculate_score(data, version_correct_answers)

        # Output result as a JSON object to stdout.
        json.dump(data, sys.stdout)

        print()

        # For debugging.
        return json.dumps(data)





