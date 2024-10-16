import math
from tokenize import group

import cv2 as cv
from imutils import contours as cutils
import numpy as np
import utils

class TextBox:
    def __init__(self, page, config, verbose_mode, debug_mode, scale):
        """
        Constructor for a new test box.

        Args:
            page (numpy.ndarray): An ndarray representing the test image.
            config (dict): A dictionary containing the config file values for
                this test box.
            verbose_mode (bool): True to run program in verbose mode, False
                otherwise.
            debug_mode (bool): True to run the program in debug mode, False
                otherwise.
            scale (float): Factor to scale image slices by.

        Returns:
            TestBox: A newly created test box.

        """
        # Args.
        self.page = page
        self.config = config
        self.verbose_mode = verbose_mode
        self.debug_mode = debug_mode
        self.scale = scale

        # Configuration values.
        self.name = config['name']
        self.type = config['type']
        self.orientation = config['orientation']
        self.multiple_responses = config['multiple_responses']
        self.x = config['x']
        self.y = config['y']
        self.rows = config['rows']
        self.columns = config['columns']
        self.groups = config['groups']
        self.bubble_width = config['bubble_width']
        self.bubble_height = config['bubble_height']
        self.x_error = config['x_error']
        self.y_error = config['y_error']

        # Set number of bubbles per question based on box orientation.
        if self.orientation == 'left-to-right':
            self.bubbles_per_q = self.columns
        elif self.orientation == 'top-to-bottom':
            self.bubbles_per_q = self.rows

        # Return values.
        self.bubbled = []
        self.unsure = []
        self.images = []
        self.status = 0
        self.error = ''

    def get_bubble_group(self, bubble):
        """
        Find and returns the group number that a bubble belong to.

        Args:
        bubble (numpy.ndarray): An ndarray representing a bubble contour.
        :param bubble:
        :return:
        int: The bubble's group number or -1 if the bubble does not belong to a group
        """
        (x,y,w,h)  = cv.boundingRect(bubble)

        #Add offsets to get coordinates in relation to the whole test images

        x += self.x
        y += self.y

        for (i,group) in enumerate(self.groups):
            if (x >= group['x_min'] - self.x_error and
                x<= group['x_max'] + self.x_error and
                y >= group['y_min'] - self.y_error and
                y <= group['y_max'] + self.y_error):
                return i

        return -1


    def is_bubble(self, contour):
        (x,y,w,h) = cv.boundingRect(contour)
        aspect_ratio = w / float(h)

        x += self.x
        y += self.y

        if (w < self.bubble_width * 0.9 or
            h < self.bubble_height * 0.9 or
            aspect_ratio < 0.7 or
            aspect_ratio > 1.3):
            return False

        for (i, group) in enumerate(self.groups):
            if (x >= group['x_min'] - self.x_error and
                    x <= group['x_max'] + self.x_error and
                    y >= group['y_min'] - self.y_error and
                    y <= group['y_max'] + self.y_error):
                return True

        return False

    def get_bubbles(self, box):
        #Find bubbles in box:
        contours, _ = cv.findContours(box, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


        bubbles = []
        for _ in range(len(self.groups)):
            bubbles.append([])

        for contour in contours:
            if self.is_bubble(contour):
                group_num = self.get_bubble_group(contour)
                bubbles[group_num].append(contour)
        return bubbles


    def box_contains_bubbles(self, box, threshold):
        im = utils.get_transform(box, threshold)
        contours, _ = cv.findContours(im, cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if self.is_bubble(contour):
                return True

        return False

    def is_box(self, contour, threshold):
        (x,y,_, _) = cv.boundingRect(contour)

        if ((self.x - self.x_error <= x <= self.x + self.x_error) and
            (self.y - self.y_error <= y <= self.y + self.y_error) and
            self.box_contains_bubbles(contour, threshold)):
            return True
        else:
            return False

    def get_box(self):
        """
        Tim va tra ve cac duong bien cho o tra loi.

        Returns:
            numpy.ndarray: An ndarray dai dien cho  khu vuc box tra loi trong khu vuc test.

        """
        # Blur and threshold the page, then find boxes within the page.
        threshold = utils.get_threshold(self.page)
        contours, _ = cv.findContours(threshold, cv.RETR_TREE,
            cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv.contourArea, reverse=True)

        # Iterate through contours until the correct box is found.
        for contour in contours:
            if self.is_box(contour, threshold):
                return utils.get_transform(contour, threshold)

        return None


    def init_questions(self):
        """
        Tao va tra ve danh sach mang trong dua tren so luong cau hoi trong group

        questions: danh sach ve nhung chuoi trong
        """
        questions = []
        if self.orientation == 'left-to-right':
            num_questions = self.rows
        elif self.orientation == 'top-to-bottom':
            num_questions = self.columns

        for _ in range(num_questions):
            questions.append([])

        return questions

    def get_question_diff(self, config):
        """
        Tim va tra ve khoang cach giua cac cau hoi
        :param config: tu dien chua gia tri config cho bubble groups
        :return: float: khoang cach giua cac cau hoi trong groups
        """
        if self.orientation == 'left-to-right':
            if self.rows == 1:
                return 0
            else:
                return (config['y_max'] - config['y_min']) / (self.rows - 1)
        elif self.orientation == 'top-to-bottom':
            if self.columns == 1:
                return 0
            else:
                return (config['x_max'] - config['x_min']) / (self.columns - 1)

    def get_question_offset(self, config):
        """
        Trả về điểm bắt đầu cho 1 nhóm bubbles trong bài ktra dựa trên cấu hình config
        :param config: 1 dictionary chứa các giá trị đầu vào cho bubble hiện tại
        :return: float: question_offset
        """
        if self.orientation == 'left-to-right':
            return config['y_min'] - self.y
        elif self.orientation == 'top-to-bottom':
            return config['x_min'] - self.x

    def get_question_num(self, bubble, diff, offset):
        """
        Tìm và trả về số câu hỏi của 1 bubble dựa trên tọa độ của nó và thông số cau trúc của nhóm câu hỏi
        :param bubble: đại diện cho 1 ô trong trắc nghiệm
        :param diff: khoảng cách các câu hỏi trong nhóm bubbles này -> khoảng cách liền kề theo hướng quét
        :param offset: Vị trí bắt đầu của nhóm bubbles. Thong số giúp xác định bubble đầu tiên của nhóm
        :return: số lươợng câu hỏi
        """

        if diff==0:
            return 0

        (x,y,_,_) = cv.boundingRect(bubble)

        if self.orientation == 'left-to-right':
            return round((y - offset) / diff)

        elif self.orientation == 'top-to-bottom':
            return round((x - offset) / diff)

    def group_by_question(self, bubbles, config):
        """
        Nhóm các bubble theo câu hỏi
        :param bubbles: danh sách các contours của các bubble
        :param config: Chứa thông số của nhóm bubbles này
        :return: Danh sach trong cac danh sach, moi ds con chua cac bubble tuong ung voi 1 cau hoi cu the
        """

        # Khoi tao cau hoi:
        questions = self.init_questions()
        diff = self.get_question_diff(config)
        offset = self.get_question_offset(config)

        for bubble in bubbles:
            question_num = self.get_question_num(bubble, diff, offset)
            questions[question_num].append(bubble)

        return questions

        #Formulas
    def get_image_coords(self, question_num, group_num, config):
        """
        Tim va tra ve toa do cua cau hoi trong bai kiem tra
        :param question_num: so thu tu cau hoi
        :param group_num: so thu tu cua nhom ma no thuoc ve
        :param config: Cau hinh cua nhom bubble
        :return: toa do x,y min max cua hinh
        """

        diff = self.get_question_diff(config)
        offset = self.get_question_offset(config)

        if self.orientation == 'left-to-right':
            question_num = question_num - (group_num * self.rows) - 1
            x_min = max(config['x_min'] - self.x - self.x_error, 0)
            x_max = config['x_max'] - self.x + self.x_error
            y_min = max((diff * question_num) + offset - (self.y_error / 2) , 0)
            y_max = y_min + self.bubble_height + self.y_error
        elif self.orientation == 'top-to-bottom':
            question_num = question_num - (group_num * self.columns) - 1
            x_min = max((diff * question_num) + offset - (self.x_error / 2) , 0)
            x_max = x_min + self.bubble_width + self.x_error
            y_min = max(config['y_min'] - self.y - self.y_error, 0)
            y_max = config['y_max'] - self.y + self.y_error

        return x_min, x_max, y_min, y_max



    def get_image_slice(self, question_num, group_num, box):
        """
        Cat va tra ve anh cat cho cau hoi khong ro
        :param question_num:   So thu tu cau hoi
        :param group_num: So thu tu nhom cau hoi
        :param box: 1 np dai dien cho box cua bai ktra
        :return: np dai dien cho cau hoi cu the trong bai test
        """

        #Get coordinages of images slice.
        config = self.groups[group_num]
        (x_max, x_min, y_min, y_max) = self.get_image_coords(question_num, group_num, config)

        #Crop image and scale:
        im = box[int(y_min) : int(y_max), int(x_min) : int(x_max)]
        im = cv.resize(im, None, fx = self.scale, fy=self.scale)

        return im

    def add_image_slice(self, question_num, group_num, box):
        """
        Them cac anh da phan chia theo tung cau hoi theo danh sach

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        """
        im = self.get_image_slice(question_num, group_num, box)
        encoded_im = utils.encode_image(im)

        # Display image to screen if program running in debug mode.
        if self.debug_mode:
            cv.imshow('', im)
            cv.waitKey()

        self.images.append(encoded_im)

    def handle_unsure_question(self, question_num, group_num, box):
        """
        Adds the image slice for the question to the list of images. Adds the
        question to the list of unsure questions.

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        """
        self.add_image_slice(question_num, group_num, box)
        self.unsure.append(question_num)
# Formulas
    def get_percent_marked(self, bubble, box):
        """
        Calculates the percentage of darkened pixels in the bubble contour.

        Args:
            bubble (numpy.ndarray): An ndarray representing the bubble.
            box (numpy.ndarray): An ndarray representing the test box image.

        Returns:
            float: The percentage of darkened pixels in the bubble contour.

        """
        # Applies a mask to the entire test box image to only look at one
        # bubble, then counts the number of nonzero pixels in the bubble.
        mask = np.zeros(box.shape, dtype='uint8')
        cv.drawContours(mask, [bubble], -1, 255, -1)
        mask = cv.bitwise_and(box, box, mask=mask)
        total = cv.countNonZero(mask)
        (x, y, w, h) = cv.boundingRect(bubble)
        area = math.pi * ((min(w, h) / 2) ** 2)

        return total / area

    def format_answer(self, bubbled):
        """
        Format answer for this question: (string, letters or numbers)
        :param bubbled: string
        :return: formatting string or "-" into unmarked
        """

        if bubbled == '':
            return '-'
        elif bubbled == '?':
            return '?'
        elif self.type == 'number':
            return bubbled
        elif self.type == 'letter':
            return ''.join([chr(int(c) + 65) for c in bubbled])


    def grade_question(self, question, question_num, group_num, box):
        """
        Grade a question and adds the result to the 'bubbled' list
        :param question: Danh sach cac bubble contour
        :param question_num: So luong cau hoi
        :param group_num: So nhom
        :param box: narray dai dien cho textbox image
        :return:
        """

        bubbled = ''
        unsure = False

        # Neu cau hoi kh duoc to, danh dau thanh unsure
        if len(question) != self.bubbles_per_q:
            unsure=True
            self.handle_unsure_question(question_num,group_num,box)
            self.bubbled.append('?')
            return

        for (i, bubble) in enumerate(question):
                percent_marked = self.get_percent_marked(bubble, box)

                if percent_marked > 0.8:
                    bubbled += str(i)

                elif percent_marked > 0.75:
                    unsure = True
                    self.handle_unsure_question(question_num,group_num,box)
                    bubbled = '?'
                    break

        if len(bubbled) > 1 and self.multiple_responses == False:
            self.handle_unsure_question(question_num, group_num, box)
            bubbled = '?'

        if self.verbose_mode and unsure == False:
            self.add_image_slice(question_num, group_num, box)

        self.bubbled.append(self.format_answer(bubbled))

    def grade_bubbles(self, bubbles, box):
        """
        Cham danh sach bubbles tu text box:
        :param bubbles:
        :param box:
        :return:
        """
        # Duyet qua tung nhom:
        for (i, group) in enumerate(bubbles):
            # Phan nhom theo cau hoi
            group = self.group_by_question(group, self.groups[i])

            for (j, question) in enumerate(group, 1):
                question_num = j + (i * len(group))
                question, _ = cutils.sort_contours(question,
                                                   method=self.orientation)

                self.grade_question(question, question_num, i, box)

    def grade(self):
        """
        Tim va cham testbox trong bai lam
        :return: data
        """
        data = {
            'status': 0,
            'error': ''
        }

        #Tim box, tim o can to, sau do tien hanh cham
        box = self.get_box()

        bubbles = self.get_bubbles(box)

        self.grade_bubbles(bubbles,box)

        data['bubbled'] = self.bubbled
        data['unsure'] = self.unsure
        data['images'] = self.images
        data['status'] = self.status
        data['error'] = self.error

        return data

