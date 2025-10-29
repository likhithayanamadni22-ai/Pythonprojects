import tkinter as tk
from tkinter import messagebox

def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if height <= 0 or weight <= 0:
            messagebox.showwarning("Invalid Input", "Please enter positive values for height and weight.")
            return

        bmi = weight / (height ** 2)
        bmi = round(bmi, 2)

        if bmi < 18.5:
            category = "Underweight 😕"
        elif 18.5 <= bmi < 24.9:
            category = "Normal Weight 🙂"
        elif 25 <= bmi < 29.9:
            category = "Overweight 😐"
        else:
            category = "Obese 😟"

        result_label.config(text=f"Your BMI is {bmi}\nCategory: {category}")

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for height and weight.")

# Create main window
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("350x300")
root.config(bg="#f7f7f7")

# Title label
title_label = tk.Label(root, text="BMI Calculator", font=("Arial", 16, "bold"), bg="#f7f7f7", fg="#333")
title_label.pack(pady=10)

# Weight input
weight_label = tk.Label(root, text="Enter Weight (kg):", font=("Arial", 12), bg="#f7f7f7")
weight_label.pack()
weight_entry = tk.Entry(root, width=20, font=("Arial", 12))
weight_entry.pack(pady=5)

# Height input
height_label = tk.Label(root, text="Enter Height (m):", font=("Arial", 12), bg="#f7f7f7")
height_label.pack()
height_entry = tk.Entry(root, width=20, font=("Arial", 12))
height_entry.pack(pady=5)

# Calculate button
calc_button = tk.Button(root, text="Calculate BMI", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=calculate_bmi)
calc_button.pack(pady=15)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="#f7f7f7", fg="#333")
result_label.pack(pady=10)

# Run the app
root.mainloop()
