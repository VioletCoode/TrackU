import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x300")
root.configure(bg="#2e2e2e")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="#3c3f41",
                foreground="white",
                fieldbackground="#3c3f41",
                rowheight=25)
style.configure("Treeview.Heading",
                background="#2e2e2e",
                foreground="white",
                font=("Arial", 12, "bold"))

tree = ttk.Treeview(root, columns=("App", "Minutes"), show="headings")
tree.heading("App", text="App Name")
tree.heading("Minutes", text="Minutes Used")
tree.pack(fill="both", expand=True)

tree.insert("", "end", values=("VS Code", 5))
tree.insert("", "end", values=("Chrome", 10))

root.mainloop()
