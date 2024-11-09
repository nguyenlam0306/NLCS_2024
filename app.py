import tkinter as tk
from tkinter import filedialog, messagebox
import json
import sys
import cv2 as cv
from main import Grader


class GraderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grader Application")

        # Image path input
        self.label_image = tk.Label(root, text="Image Path:")
        self.label_image.grid(row=0, column=0, padx=10, pady=10)

        self.entry_image = tk.Entry(root, width=40)
        self.entry_image.grid(row=0, column=1, padx=10, pady=10)

        self.button_browse = tk.Button(root, text="Browse", command=self.browse_image)
        self.button_browse.grid(row=0, column=2, padx=10, pady=10)

        # Information label
        self.label_image_contains = tk.Label(
            root, text="Ảnh rõ nét đường biên và mã QR, phải là png hoặc jpg."
        )
        self.label_image_contains.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Verbose mode checkbox
        self.verbose_var = tk.BooleanVar()
        self.checkbox_verbose = tk.Checkbutton(
            root, text="Verbose Mode", variable=self.verbose_var
        )
        self.checkbox_verbose.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

        # Debug mode checkbox
        self.debug_var = tk.BooleanVar()
        self.checkbox_debug = tk.Checkbutton(
            root, text="Debug Mode", variable=self.debug_var
        )
        self.checkbox_debug.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        # Scale input
        self.label_scale = tk.Label(root, text="Scale:")
        self.label_scale.grid(row=5, column=0, padx=10, pady=10)

        self.entry_scale = tk.Entry(root, width=10)
        self.entry_scale.grid(row=5, column=1, padx=10, pady=10)

        # Grade button
        self.button_grade = tk.Button(root, text="Grade", command=self.grade)
        self.button_grade.grid(row=6, column=0, columnspan=3, pady=20)

        # Output Text
        self.text_output = tk.Text(root, height=10, width=50)
        self.text_output.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])
        if file_path:
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, file_path)

    def grade(self):
        image_name = self.entry_image.get()
        verbose_mode = self.verbose_var.get()
        debug_mode = self.debug_var.get()
        scale = self.entry_scale.get()

        if not image_name:
            messagebox.showerror("Error", "Please select an image.")
            return

        try:
            scale = float(scale) if scale else 1.0  # Convert scale to float
        except ValueError:
            messagebox.showerror("Error", "Scale must be a valid number.")
            return

        try:
            # Grader function logic
            grader = Grader()
            result = grader.grade(image_name, verbose_mode, debug_mode, scale)

            # Display result in the text box
            self.text_output.delete(1.0, tk.END)  # Clear previous output
            self.text_output.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = GraderApp(root)
    root.mainloop()
