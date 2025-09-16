import os
import threading
import subprocess
from tkinter import Tk, Label, Entry, Button, messagebox
from tkinter.ttk import Progressbar

found = False
stop_search = False
lock = threading.Lock()

def open_file(file_path):
    try:
        if os.name == 'nt': 
            os.startfile(file_path)
        elif os.name == 'posix': 
            subprocess.call(('xdg-open', file_path)) 
        print(f"✅ File opened: {file_path}")
    except Exception as e:
        print(f"❌ Error opening file: {e}")

def search_file_in_directory(directory, target_filename):
    global found, stop_search

    if found or stop_search:
        return

    try:
        for entry in os.listdir(directory):
            if found or stop_search:
                return

            full_path = os.path.join(directory, entry)

            if os.path.isfile(full_path) and entry == target_filename:
                with lock:
                    found = True
                    print(f"✅ File found at: {full_path}")
                    open_file(full_path)
                return

            elif os.path.isdir(full_path):
                threading.Thread(target=search_file_in_directory, args=(full_path, target_filename)).start()

    except PermissionError:
        pass

def search_file(root_directory, target_filename):
    global found, stop_search
    found = False
    stop_search = False
    search_file_in_directory(root_directory, target_filename)

def on_search():
    root_dir = entry_dir.get().strip()
    target_file = entry_file.get().strip()

    if not os.path.isdir(root_dir):
        messagebox.showerror("Error", "❌ Invalid directory path.")
        return

    if not target_file:
        messagebox.showerror("Error", "❌ Please enter a file name to search.")
        return

    print(f"🔍 Searching for '{target_file}' in '{root_dir}' ...")
    status_label.config(text="Searching... Please wait.")
    progress_bar.start()

    threading.Thread(target=lambda: threaded_search(root_dir, target_file)).start()

def threaded_search(root_dir, target_file):
    search_file(root_dir, target_file)
    progress_bar.stop()
    if not found and not stop_search:
        status_label.config(text="❌ File not found.")
    elif stop_search:
        status_label.config(text="❌ Search cancelled.")
    else:
        status_label.config(text="✅ File found and opened.")

def cancel_search():
    global stop_search
    stop_search = True
    progress_bar.stop()
    status_label.config(text="❌ Search cancelled.")
    print("❌ Search cancelled by user.")

def create_gui():
    global entry_dir, entry_file, status_label, progress_bar

    window = Tk()
    window.title("Multithreaded File Search and Open")
    window.geometry("500x350")

    Label(window, text="Enter Root Directory Path:", font=('Arial', 12)).pack(pady=5)
    entry_dir = Entry(window, width=50)
    entry_dir.pack(pady=5)

    Label(window, text="Enter Filename to Search:", font=('Arial', 12)).pack(pady=5)
    entry_file = Entry(window, width=50)
    entry_file.pack(pady=5)

    status_label = Label(window, text="", font=('Arial', 12))
    status_label.pack(pady=10)

    progress_bar = Progressbar(window, mode='indeterminate')
    progress_bar.pack(pady=10, fill='x', padx=20)

    search_button = Button(window, text="Search File", font=('Arial', 12), command=on_search)
    search_button.pack(pady=5)

    cancel_button = Button(window, text="Cancel Search", font=('Arial', 12), command=cancel_search)
    cancel_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_gui()