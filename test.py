# -*- coding: utf-8 -*-  
import tkinter as tk
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self,master = None):
        tk.Frame.__init__(self,master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.quitButton = tk.Button(self, text = 'quit', command = self.quit)
        self.quitButton.grid()


app = Application()
app.master.title('hello tkinter')
app.mainloop()
