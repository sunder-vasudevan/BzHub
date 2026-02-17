import tkinter as tk

root = tk.Tk()
root.title("Tkinter Test")
root.geometry("400x200")

label = tk.Label(root, text="If you see this, Tkinter is working!", font=("Arial", 14), fg="blue")
label.pack(pady=40)

entry = tk.Entry(root)
entry.pack(pady=10)

root.mainloop()
