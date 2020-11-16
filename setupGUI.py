from tkinter import *
import os
from tkinter import filedialog
import PIL.Image
from PIL import ImageTk
from tkinter import messagebox
from ctypes import windll, Structure, c_long, byref


if os.name == "nt":
    from ctypes import windll, pointer, wintypes
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
root = Tk()
root.title("Setup")
root.geometry("400x520")
root.resizable(0,0)

user = windll.user32
frameMain = Frame(root,bg="white", width=400,height=520)
frameMain.pack()
coordsList = []
C = Canvas(frameMain, bg="white", height=474, width=400, cursor="crosshair") #making Canvas global variable
name = filedialog.askopenfilename(initialdir = "/",title = "Select Picture for Diagram",filetypes = (("gif files","*.gif"),("all files","*.*"))) #reading file name
#name = "res\\6New.gif"

def processxy(event):
    xy = 'x=%s  y=%s' % (event.x, event.y)
    print(xy)
    coordsList.append([event.x-8,event.y-7])
    #C.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill = 'red')
    C.create_text(event.x, event.y, fill = 'red', text = str(len(coordsList)))

def process():
    MsgBox = messagebox.askquestion ('Exit Application','Are you sure all wanted valve locations were selected. This will override any previous setup data!',icon = 'warning')
    if MsgBox == 'yes':
        #writing data to contentWrite variable
        contentWrite = ""
        contentWrite = contentWrite + name + "\n"
        contentWrite = contentWrite + str(len(coordsList)) + "\n"
        for val in coordsList:
            contentWrite = contentWrite + ("%s,%s" % (val[0],val[1]) ) + "\n"
            
        file = open("res//setup.txt",'w')
        file.write(contentWrite)
        file.close()
        messagebox.showinfo("Success", "Data saved in setup file! Press OK to close this program")
        root.destroy()
        raise SystemExit(0) #ending program

#functionality to use arrw keys for movement
    
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]
    
def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return [pt.x, pt.y]

def keyR(event):
    #frameMain.focus_set()
    #print(event.x,event.y)
    pos = queryMousePosition()
    user.SetCursorPos(pos[0]+5,pos[1])
def keyL(event):
    pos = queryMousePosition()
    user.SetCursorPos(pos[0]-5,pos[1])
def keyU(event):
    pos = queryMousePosition()
    user.SetCursorPos(pos[0],pos[1]-5)
def keyD(event):
    pos = queryMousePosition()
    user.SetCursorPos(pos[0],pos[1]+5)
    
#inital canvas setup
img = PIL.Image.open(name)
img = img.resize((400,474), PIL.Image.ANTIALIAS)
#img.save(name, quality=100)
filename = ImageTk.PhotoImage(img)
C.create_image(0, 0, image=filename, anchor=NW,tag="main")
C.pack(side="top")

C.tag_bind('main', '<Button-1>', processxy)
root.focus_set()
root.bind("<Right>",keyR)
root.bind("<Left>",keyL)
root.bind("<Up>",keyU)
root.bind("<Down>",keyD)
doneBtn = Button(frameMain, relief = GROOVE, text="Done",width=400, command=lambda:process())
doneBtn.pack(side="bottom")
messagebox.showinfo("Setup", "Click on the image where you want a valve button to be placed. Press done when finished.")



root.mainloop()
