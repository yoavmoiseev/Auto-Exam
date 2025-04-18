# Tkinter GUI for selecting an exam file from a specified folder
import tkinter as tk
from tkinter import messagebox  # Import tkinter for GUI elements
import os  # Import library for handling file paths 

#================================================================================================
def select_exam_file(exams_folder_name = "Exams"):
    """Opens a GUI form where the user can select a file from the 'Exams' folder.
        returns the full path of the selected file.
    """
    exams_folder = os.path.join(os.path.dirname(__file__), exams_folder_name)  # Path to 'Exams' folder

    # Check if the folder exists
    if not os.path.exists(exams_folder):
        messagebox.showerror("Error", f"Folder '{exams_folder}' not found!")
        return None

    # Get the list of .txt files in the folder
    exam_files = [f for f in os.listdir(exams_folder) if f.endswith('.txt')]

    if not exam_files:
        messagebox.showwarning("No Exams Found", "No exam files found in the 'Exams' folder.")
        return None

    # Function to handle selection
    def on_select():
        """Handles the selection of a file and closes the window."""
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select an exam file.")
            return
        selected_file.set(exam_files[selected_index[0]])  # Store selected file
        root.destroy()  # Close window

    # Create the main GUI window
    root = tk.Tk()
    root.title("Select Exam File")
    root.geometry("300x250")

    # Create a StringVar to store the selected file
    selected_file = tk.StringVar()

    # Create and pack a label
    tk.Label(root, text="Select an Exam File:", font=("Arial", 12)).pack(pady=10)

    # Create and pack a listbox
    listbox = tk.Listbox(root, selectmode=tk.SINGLE, font=("Arial", 10), height=len(exam_files))
    for file in exam_files:
        listbox.insert(tk.END, file)
    listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # Create and pack a select button
    tk.Button(root, text="Select", command=on_select).pack(pady=10)

    # Run the event loop
    root.mainloop()

    # Return the full file path if a file was selected
    return os.path.join(exams_folder, selected_file.get()) if selected_file.get() else None
#================================================================================================
