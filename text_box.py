import math
import cv2 as cv
from imutils import contours as cutils
import numpy
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
        Finds and returns the contour for this test answer box.

        Returns:
            numpy.ndarray: An ndarray representing the answer box in
                the test image.

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


