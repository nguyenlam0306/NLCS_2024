from tkinter import filedialog, Label, Button, Tk
from image_processing import process_image
from grading import load_answer_key, grade_student, save_results


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần mềm chấm điểm trắc nghiệm")

        self.label = Label(root, text="Chọn ảnh phiếu trả lời để chấm")
        self.label.pack()

        self.load_button = Button(root, text="Tải ảnh", command=self.load_image)
        self.load_button.pack()

        self.result_label = Label(root, text="")
        self.result_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            answers = process_image(file_path)
            answer_key = load_answer_key()
            score = grade_student(answers, answer_key)
            self.result_label.config(text=f"Kết quả: {score}/50")
            save_results("SBD123", score)
