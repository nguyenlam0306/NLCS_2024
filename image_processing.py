import cv2
import numpy as np


def process_image(image_path):
    # Đọc ảnh
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Nhị phân hóa ảnh
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Phát hiện các ô tròn đáp án
    circles = cv2.HoughCircles(binary_image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=10,
                               param1=50, param2=30, minRadius=10, maxRadius=20)

    # Xử lý kết quả phát hiện
    answers = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Kiểm tra xem ô có được tô hay không
            if is_filled(binary_image, x, y, r):
                answers.append((x, y))  # Lưu lại tọa độ các ô được tô

    return answers


def is_filled(image, x, y, radius):
    # Kiểm tra tỷ lệ điểm đen trong vòng tròn
    mask = np.zeros_like(image)
    cv2.circle(mask, (x, y), radius, 255, -1)
    filled_ratio = np.sum(image[mask == 255]) / (np.pi * radius * radius)
    return filled_ratio > 0.5  # Trả về True nếu ô được tô đậm
