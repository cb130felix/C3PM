import tkinter as tk
from tkinter import *

root = tk.Tk()

canvas = tk.Canvas(root, height=700, width=700)
canvas.pack()

frame = tk.Frame(root, bg='green')
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

root.mainloop()