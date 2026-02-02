# Tkinter GUI for selecting an exam file from a specified folder
import tkinter as tk
from tkinter import messagebox  # Import tkinter for GUI elements
import os  # Import library for handling file paths 
import consts

#================================================================================================
def add_max_questions_field(root):
    """Adds a field to the GUI for the user to input the maximum number of questions.
       Returns the StringVar associated with the entry field."""
    # Create a frame to hold the label and entry field on the same line
    frame = tk.Frame(root)
    frame.pack(pady=5, padx=10, fill=tk.X)

    # Create a label for the max questions field
    tk.Label(frame, text="Limit the number of exam questions:", font=("Arial", 10)).pack(side="left", padx=5)

    # Create an entry widget for the user to input the max number of questions
    max_questions_var = tk.StringVar(value="1000")  # Default value is '1000'
    max_questions_entry = tk.Entry(frame, textvariable=max_questions_var, font=("Arial", 10), width=5)
    max_questions_entry.pack(side="left")
    
    return max_questions_var
#================================================================================================
def shuffle_questions(root):
    """Check-box for Shuffle Exam option"""
    # Create a frame to hold the label and entry field on the same line
    frame = tk.Frame(root)
    frame.pack(pady=5, padx=10, fill=tk.X)

    # Create a label for Shuffle exam
    tk.Label(frame, text="Shuffle Exam:", font=("Arial", 10)).pack(side="left", padx=5)

    # Create a BooleanVar to track the state of the checkbox
    shuffle_var = tk.BooleanVar(value=True)  # Default checked (True)

    # Create a Checkbutton and bind it to the BooleanVar
    shuffle_entry = tk.Checkbutton(frame, variable=shuffle_var)
    shuffle_entry.pack(side="left")

    # Return the BooleanVar so its value can be accessed
    return shuffle_var
#================================================================================================
def select_exam_file(exams_folder_name="Exams"):
    """Opens a GUI form where the user can select a file from the 'Exams' folder.
       Returns the full path of the selected file and the max questions value.
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

        # Validate the max questions field
        try:
            max_questions = int(max_questions_var.get())  # Try to convert to an integer
            if max_questions <= 0:  # Ensure the value is positive
                raise ValueError("Max questions must be a positive integer.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for max questions.")
            return

        selected_file.set(exam_files[selected_index[0]])  # Store selected file
        root.destroy()  # Close window

    # Create the main GUI window
    root = tk.Tk()
    root.title("Select Exam File")
    root.geometry("300x600")  # Adjusted height to accommodate the new field

    # Create a StringVar to store the selected file
    selected_file = tk.StringVar()

    # Add the max questions field
    max_questions_var = add_max_questions_field(root)

    # Add the shuffle-exam check-botton
    shuffle_var = shuffle_questions(root)
    

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

    # Return the full file path and max questions value
    return os.path.join(exams_folder, selected_file.get()) if selected_file.get() else None, \
        int(max_questions_var.get()), shuffle_var.get() # Return the max questions value,
                                                   # shuffle option value
#================================================================================================
