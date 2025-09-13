import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import win32gui
from collections import defaultdict
import csv
import os

# -------------------- Tracker Logic --------------------
def get_active_window():
    """Return the title of the current active window."""
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)
    return title if title else "Unknown"

# Current session usage
usage_time = defaultdict(int)
# Previous total usage (from file, loaded into usage_time)
last_window = None
last_time = time.time()
tracking = True  # Auto-start tracking

# -------------------- Load Previous Usage --------------------
def load_previous_usage():
    """Load previous usage from persistent CSV if it exists."""
    file_path = "usage_data.csv"
    if os.path.exists(file_path):
        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                app, time_str = row
                h, m, s = 0, 0, 0
                parts = time_str.split()
                for part in parts:
                    if part.endswith("h"):
                        h = int(part[:-1])
                    elif part.endswith("m"):
                        m = int(part[:-1])
                    elif part.endswith("s"):
                        s = int(part[:-1])
                total_secs = h*3600 + m*60 + s
                usage_time[app] = total_secs

load_previous_usage()

# -------------------- GUI Functions --------------------
def update_usage_gui():
    """Update the Treeview table with app usage and highlight active app."""
    global last_window, last_time, usage_time

    if tracking:
        current_window = get_active_window()
        current_time = time.time()

        if last_window:
            usage_time[last_window] += current_time - last_time

        last_window = current_window
        last_time = current_time
    else:
        current_window = None

    # Clear table
    for row in tree.get_children():
        tree.delete(row)

    # Insert updated usage with highlighting
    for app, secs in usage_time.items():
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        time_str = f"{h}h {m}m {s}s"
        if app == current_window:
            tree.insert("", "end", values=(app, time_str), tags=("active",))
        else:
            tree.insert("", "end", values=(app, time_str))

    tree.tag_configure("active", background="#007acc", foreground="white")

    # Repeat every second
    root.after(1000, update_usage_gui)

def stop_tracking():
    global tracking
    tracking = False
    messagebox.showinfo("TrackU", "Tracking stopped!")

def save_report():
    """Save app usage to CSV file at user-selected location AND update persistent file."""
    # Save to user-selected location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile="app_usage_report.csv",
        title="Save Report As"
    )

    if file_path:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["App Name", "Time Used"])
            for app, secs in usage_time.items():
                h = int(secs // 3600)
                m = int((secs % 3600) // 60)
                s = int(secs % 60)
                time_str = f"{h}h {m}m {s}s"
                writer.writerow([app, time_str])
        messagebox.showinfo("TrackU", f"Report saved as:\n{file_path}")

    # Save to persistent file
    with open("usage_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["App Name", "Time Used"])
        for app, secs in usage_time.items():
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            time_str = f"{h}h {m}m {s}s"
            writer.writerow([app, time_str])

def update_clock():
    """Update the real-time clock label with DATE, TIME, DAY on separate lines."""
    current_date = time.strftime("%d %b %Y")
    current_time = time.strftime("%H:%M:%S")
    current_day  = time.strftime("%A")
    clock_label.config(text=f"DATE: {current_date}\nTIME: {current_time}\nDAY: {current_day}")
    root.after(1000, update_clock)

# -------------------- GUI Setup --------------------
root = tk.Tk()
root.title("TrackU")
root.geometry("650x500")
root.configure(bg="#2e2e2e")  # Dark background

# Style for Treeview (dark mode)
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
style.map("Treeview", background=[("selected", "#007acc")])

# Title label
title_label = tk.Label(root, text="TrackU",
                       font=("Arial", 16, "bold"),
                       bg="#2e2e2e", fg="white")
title_label.pack(pady=5)

# Clock label (top-right corner)
clock_label = tk.Label(root, text="", font=("Arial", 12),
                       bg="#2e2e2e", fg="white", justify="right")
clock_label.pack(anchor="ne", padx=10)

# Frame for table
table_frame = tk.Frame(root, bg="#2e2e2e")
table_frame.pack(pady=10, fill="both", expand=True)

# Scrollbar
scrollbar = tk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

# Treeview (table)
tree = ttk.Treeview(table_frame, columns=("App", "Time"), show="headings",
                    yscrollcommand=scrollbar.set)
tree.heading("App", text="App Name")
tree.heading("Time", text="Time Used")
tree.column("App", width=400)
tree.column("Time", width=200, anchor="center")
tree.pack(fill="both", expand=True)

scrollbar.config(command=tree.yview)

# Buttons
btn_frame = tk.Frame(root, bg="#2e2e2e")
btn_frame.pack(pady=10)

btn_bg = "#007acc"
btn_fg = "white"

stop_btn = tk.Button(btn_frame, text="Stop Tracking", command=stop_tracking,
                     width=15, bg=btn_bg, fg=btn_fg)
stop_btn.grid(row=0, column=0, padx=5)

save_btn = tk.Button(btn_frame, text="Save Report", command=save_report,
                     width=15, bg=btn_bg, fg=btn_fg)
save_btn.grid(row=0, column=1, padx=5)

# -------------------- Start trackers --------------------
update_usage_gui()  # Start app usage tracking automatically
update_clock()      # Start real-time clock

# Run the GUI
root.mainloop()
