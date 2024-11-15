import cv2
import os

# Đọc file ảnh
image_path = r"/train/images/50cau/test-vers-50q-01.jpg"

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

        # Phát hiện cạnh sử dụng Canny
        edges = cv2.Canny(gray, 50, 150)

        # Tìm các contours (đường biên) trên ảnh
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Duyệt qua các contours để tìm mã QR hoặc vùng trả lời
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Kiểm tra kích thước để loại bỏ các vùng nhiễu nhỏ
            if w > 50 and h > 50:
                print(f"Tọa độ tìm thấy: x={x}, y={y}, width={w}, height={h}")
                # Vẽ hình chữ nhật lên vùng được phát hiện
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Đặt kích thước ảnh hiển thị vừa với màn hình
        screen_width = 800
        screen_height = 600
        resized_image = cv2.resize(image, (screen_width, screen_height))

        # Hiển thị ảnh đã thay đổi kích thước
        cv2.imshow("Detected", resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
