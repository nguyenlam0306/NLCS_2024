from _datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import sys
import os
import cv2 as cv
from main import Grader


class GraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grader Application")

        # Image path input
        self.label_image = tk.Label(root, text="Select Images:")
        self.label_image.grid(row=0, column=0, padx=10, pady=10)

        self.entry_image = tk.Entry(root, width=50)
        self.entry_image.grid(row=0, column=1, padx=10, pady=10)

        self.button_browse = tk.Button(root, text="Browse", command=self.browse_images)
        self.button_browse.grid(row=0, column=2, padx=10, pady=10)

        # Information label
        self.label_info = tk.Label(
            root, text="Chọn nhiều file ảnh (.png hoặc .jpg) để chấm điểm."
        )
        self.label_info.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Verbose mode checkbox
        self.verbose_var = tk.BooleanVar()
        self.checkbox_verbose = tk.Checkbutton(
            root, text="Verbose Mode", variable=self.verbose_var
        )
        self.checkbox_verbose.grid(row=3, column=0, padx=10, pady=10)

        # Debug mode checkbox
        self.debug_var = tk.BooleanVar()
        self.checkbox_debug = tk.Checkbutton(
            root, text="Debug Mode", variable=self.debug_var
        )
        self.checkbox_debug.grid(row=4, column=0, padx=10, pady=10)

        # Scale input
        self.label_scale = tk.Label(root, text="Scale:")
        self.label_scale.grid(row=5, column=0, padx=10, pady=10)

        self.entry_scale = tk.Entry(root, width=10)
        self.entry_scale.grid(row=5, column=1, padx=10, pady=10)

        # Grade button
        self.button_grade = tk.Button(root, text="Grade All", command=self.grade_all)
        self.button_grade.grid(row=6, column=1, pady=20)

        self.grader = Grader()
        self.selected_files = []

    def browse_images(self):
        """Chọn nhiều file ảnh."""
        self.selected_files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.png *.jpg")]
        )
        if self.selected_files:
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, ", ".join(self.selected_files))

    def grade_all(self):
        """Chấm điểm cho tất cả các file đã chọn và lưu kết quả."""
        if not self.selected_files:
            messagebox.showerror("Error", "No images selected.")
            return

        verbose_mode = self.verbose_var.get()
        debug_mode = self.debug_var.get()
        scale = self.entry_scale.get() if self.entry_scale.get() else None

        results = []
        for image_path in self.selected_files:
            print(f"Grading {image_path}...")
            result = self.grader.grade(image_path, verbose_mode, debug_mode, scale)
            if result:
                results.append(json.loads(result))

        # Lưu kết quả vào file JSON
        # Tạo thư mục nếu chưa tồn tại
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        # Định dạng tên file theo ngày giờ hiện tại
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)


        with open(file_path, 'w') as f:
            json.dump(results, f, indent=4)

        messagebox.showinfo("Success", f"Results saved to {output_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraderApp(root)
    root.mainloop()
