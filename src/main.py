import cv2
import pytesseract
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

# Cấu hình Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Hàm phát hiện đáp án từ ảnh
def detect_answers(image, correct_answers):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    answer_boxes = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])

    answers = []
    for idx, cnt in enumerate(answer_boxes):
        x, y, w, h = cv2.boundingRect(cnt)
        roi = thresh[y:y + h, x:x + w]

        answer_text = pytesseract.image_to_string(roi, config='--psm 10')
        answers.append(answer_text.strip())

    results = []
    for i, answer in enumerate(answers):
        result = f"Câu {i + 1}: {answer} - {'Đúng' if answer == correct_answers[i] else 'Sai'}"
        results.append(result)

    return results


# Hàm xử lý từ file ảnh
def process_from_file(image_path, correct_answers):
    image = cv2.imread(image_path)
    results = detect_answers(image, correct_answers)
    return results


# Giao diện chính với Tkinter
class ExamCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần mềm chấm điểm trắc nghiệm")

        self.correct_answers = []
        self.results = []

        # Nhập mã đề và số câu hỏi
        self.label_code = tk.Label(root, text="Mã đề:")
        self.label_code.pack()

        self.entry_code = tk.Entry(root)
        self.entry_code.pack()

        self.label_num = tk.Label(root, text="Số câu hỏi:")
        self.label_num.pack()

        self.entry_num = tk.Entry(root)
        self.entry_num.pack()

        # Nhập đáp án đúng cho từng câu
        self.label_answers = tk.Label(root, text="Nhập đáp án đúng:")
        self.label_answers.pack()

        self.text_answers = tk.Text(root, height=5)
        self.text_answers.pack()

        # Nút chọn file và chấm điểm
        self.button_choose_file = tk.Button(root, text="Chọn file bài thi", command=self.choose_file)
        self.button_choose_file.pack()

        self.button_process = tk.Button(root, text="Chấm điểm", command=self.check_exam)
        self.button_process.pack()

        # Hiển thị kết quả
        self.label_results = tk.Label(root, text="Kết quả:")
        self.label_results.pack()

        self.text_results = tk.Text(root, height=10)
        self.text_results.pack()

    def choose_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            messagebox.showinfo("File đã chọn", f"Đã chọn file: {self.file_path}")

    def check_exam(self):
        try:
            # Lấy mã đề và đáp án đúng
            self.correct_answers = self.text_answers.get("1.0", "end-1c").splitlines()
            exam_code = self.entry_code.get()

            # Kiểm tra số câu hỏi
            num_questions = int(self.entry_num.get())
            if len(self.correct_answers) != num_questions:
                messagebox.showerror("Lỗi", "Số lượng đáp án không khớp với số câu hỏi.")
                return

            # Gọi hàm xử lý file
            self.results = process_from_file(self.file_path, self.correct_answers)

            # Hiển thị kết quả
            self.text_results.delete("1.0", tk.END)
            for result in self.results:
                self.text_results.insert(tk.END, result + "\n")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamCheckerApp(root)
    root.mainloop()
