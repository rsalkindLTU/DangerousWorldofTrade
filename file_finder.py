import tkinter
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

def find():
    # Do not show the root item
    root = tkinter.Tk()
    root.withdraw()

    name = askopenfilename(initialdir="C:\\Users",
                            filetypes=(('Log files', '*.log'),('All Files', '*.*')),
                            title="Please choose an Elite: Dangerous Journal file.")
    return name

def notify():
    # Do not show the default window.
    root = tkinter.Tk()
    root.withdraw()

    statement = '''
    Please find the directory with a journal file in it on the next screen.
    Select any one of the journal files. It does not matter.
    On Windows: C:\\Users\\<username>\\Saved Games\\Frontier Developments\\Elite Dangerous\\<Journal. . .>
    For *nix: Wherever the saved games file is.
    ( Probably '\\usr\\<username>\\Saved Games\\' or something. I dunno. )
    '''
    messagebox.showinfo("DangerousWorldOfTrade", statement)

def find_journal_directory():
    notify()
    return find()
