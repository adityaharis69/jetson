import sys
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import os
from pathlib import Path
from Camera import*
from tkinter import Tk , Canvas, Entry, Text, Button, PhotoImage

class jetsonUIClass():
    def __init__(self,root):
        self.root=root
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / Path(r"E:\JETSON\Tkinter-Designer\tkdesigner\build\assets\frame0")
        self.root.geometry("1440x980")
        self.root.configure(bg = "#FFFFFF")
        self.root.title("NEURABOT AI")
        self.StatusRuning =True
        
        
        self.canvas = Canvas(
            self.root,
            bg = "#FFFFFF",
            height = 980,
            width = 1440,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            0.0,
            0.0,
            1440.0,
            116.0,
            fill="#111827",
            outline="",
            tags="menuFrame"
            )
        

        self.canvas.create_rectangle(
            0.0,
            114.0,
            1440.0,
            980.0,
            fill="#8F8E8E",
            outline="",
            tags="cameraFrame"
            )
    
    
        
        
if __name__ == "__main__":
    root =Tk()
    app=jetsonUIClass(root)
    root.mainloop()

