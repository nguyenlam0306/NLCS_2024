import cv2
import os

# Đọc file ảnh
image_path = r"E:\Projects\exam_grading_system\train\images\6cau\vers-A-6q.jpg"

# Kiểm tra xem file có tồn tại không
if not os.path.exists(image_path):
    print("File không tồn tại:", image_path)
else:
    image = cv2.imread(image_path)
    if image is None:
        print("Không thể đọc file:", image_path)
    else:
        print("Đọc ảnh thành công!")

        # Chuyển sang ảnh xám để xử lý
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Ngưỡng hóa ảnh (binarization)
        _, binary_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Resize ảnh để vừa với màn hình
        screen_width = 1280  # Đặt chiều rộng màn hình của bạn
        screen_height = 720  # Đặt chiều cao màn hình của bạn

        # Lấy kích thước ảnh gốc
        height, width = binary_image.shape

        # Tính toán tỷ lệ co để vừa với màn hình
        scale_width = screen_width / width
        scale_height = screen_height / height
        scale = min(scale_width, scale_height)  # Chọn tỷ lệ nhỏ hơn để giữ nguyên tỷ lệ ảnh

        # Resize ảnh dựa trên tỷ lệ đã tính
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_image = cv2.resize(binary_image, (new_width, new_height))

        # Hiển thị ảnh đã resize
        cv2.imshow("Resized Thresholded Image", resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
