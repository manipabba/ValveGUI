from tkinter import *
import tkinter.simpledialog as simpledialog
import serial
import _thread
from tkinter import messagebox
from tkinter import filedialog
import time
import os
from timeit import default_timer as timer
import PIL.Image
from PIL import ImageTk
from functools import partial

'''
#Mani Pabba
#Last Updated: 1/7/2020
Notes:
On state represented by lowercase letters, turns pin to HIGH voltage, representing closed state of valve
Off state represented by uppercase letters, turns pin to LOW voltage, representing open state of valve
'''

#Global Variables
#ser = serial.Serial('COM3', baudrate=9600, timeout = 1)
#print(ser.name) #testing to see if connected

root = Tk()

valP = 32

#adjusting program for DPI of differnt systems
'''
if os.name == "nt":
    from ctypes import windll, pointer, wintypes
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
'''

#------------loading in all values from setup.txt------------
file = open("res\\setup.txt","r") #reading file
contents = ""
if file.mode == "r":
    contents = file.read()
contentsDat = contents.split("\n")
LD_filename = contentsDat[0] #setting file name of picture resource
numValves = int(contentsDat[1]); #setting number of valves
varLocations = []
#setting location data for each valve
for i in range(2,2+numValves):
    varLocations.append(contentsDat[i].split(","))
varLocations  = [list(map(int, lst)) for lst in varLocations] #converting from str to int

#varLocations = [[77,86],[303,91],[11,225],[11,275],[11,325],[11,375],[90,420],[182,420],[246,420],[314,420]] #coords for Hesam's setup, uses 10s valves
#------------------------------------------------------------
#defining radiobutton variables as global
varList = []
for i in range(0,numValves):
    varList.append(IntVar())

#generating dictionaries
valveOnDict = {0:"EMPTY"}
valveOffDict = {0:"EMPTY"}

for i in range(1,numValves+1):
    valveOnDict[i] = bytes(chr(96+i),'utf-8')
    valveOffDict[i] = bytes(chr(64+i),'utf-8')

#inverse maps
inv_On = {v: k for k, v in valveOnDict.items()}
inv_Off = {v: k for k, v in valveOffDict.items()}

def send(num):
    #ser.write(num)
    #data = ser.readline().decode('ascii')
    #print(data.strip())
    print(num)
    updateRadioButtons(num)
    
def updateRadioButtons(num):
    #upodating buttons based on num val passed in from send()
    try:
        if str(num).islower() is True:
            varList[inv_On[num] - 1].set(1)
        else:
            varList[inv_Off[num] - 1].set(0)

    except KeyError:
        print("value out of dictonary sent")
#exception handeler helper method to processCommand2()
def exceptionHandler(btn, btn_text, text, TWindow):
    text = text.strip()
    btn.config(state='disabled')
    btn_text.set("Running Command")
    textData = text.split("\n")
    timePrevious = 0 #previous time
    try:
        #making sure first line doesn't have x or y
        lineCheck = textData[0].split()[1]
        if 'x' in lineCheck or 'y' in lineCheck:
            raise IOError
        for line in textData:
            timeDelay = float(line.split()[0]) #time of state
            sequence = str(line.split()[1]) #state values

            #making sure 10 states are given
            if(len(sequence) != numValves):
                raise IndentationError
            
            #running through each value in string
            for valveIdx in range(1,len(sequence)+1):
                if sequence[valveIdx-1] != '1' and sequence[valveIdx-1] != '0' and sequence[valveIdx-1] != 'x' and sequence[valveIdx-1] != 'y':
                    raise IndexError
               
    #error handeling
    except IOError:
        btn_text.set("Error")
        messagebox.showinfo("Command Failiure", "Cannot use x or y in the first line!")
        return False
    except IndentationError:
        btn_text.set("Error")
        messagebox.showinfo("Command Failiure", "Must type states for all valves. %d states not given!" % numValves)
        return False
    except IndexError:
        btn_text.set("Error")
        messagebox.showinfo("Command Failiure", "Bad command syntax! Refer to help if needed.")
        return False
    except ValueError:
        btn_text.set("Error")
        messagebox.showinfo("Command Failiure", "Time must be an integer or decimal")
        return False
        
    btn.config(state='normal') #enabling command button
    btn_text.set("Send Command")   
    return True

#updated process command for text window
def processCommand2(btn, btn_text, text, TWindow):
    #checking if all command syntax is good
    if exceptionHandler(btn, btn_text, text, TWindow) is True:
        start = timer()
        text = text.strip()
        btn.config(state='disabled')
        btn_text.set("Running Command")
        textData = text.split("\n")
        timePrevious = 0 #previous time
        linePrev = "" #flipstate stuff (not used right now)
        #establishing inital states
        currFlipState = []
        for idx in range(0,numValves):
            #currFlipState[idx] = textData[0].split()[1][idx]
            currFlipState.append(textData[0].split()[1][idx])
        for line in textData:
            timeDelay = float(line.split()[0]) #time of state
            sequence = str(line.split()[1]) #state values
            
            time.sleep(timeDelay - timePrevious)
            timePrevious = timeDelay #updating previous time counter
            #XY feature not working yet and is slowing down execution
            #running through each value in string
            for valveIdx in range(1,len(sequence)+1):
                #if 1
                if sequence[valveIdx-1] == '1':
                    _thread.start_new_thread(send, (valveOnDict[int(valveIdx)],)) #threading to increase runtime efficiency
                    currFlipState[valveIdx-1] = '1' #updating flipState

                #if 0
                elif sequence[valveIdx-1] == '0':
                    _thread.start_new_thread(send, (valveOffDict[int(valveIdx)],))
                    currFlipState[valveIdx-1] = '0' #updating flipState
                #if x
                elif sequence[valveIdx-1] == 'x':
                    sequencePrev = str(linePrev.split()[1])
                    if currFlipState[valveIdx-1] == '1':
                        _thread.start_new_thread(send, (valveOnDict[int(valveIdx)],)) #threading to increase runtime efficiency
                        currFlipState[valveIdx-1] = '1' #updating flipState
                    elif currFlipState[valveIdx-1] == '0':
                        _thread.start_new_thread(send, (valveOffDict[int(valveIdx)],))
                        currFlipState[valveIdx-1] = '0' #updating flipState
                #if y
                elif sequence[valveIdx-1] == 'y':
                    sequencePrev = str(linePrev.split()[1])
                    if currFlipState[valveIdx-1] == '0':
                        _thread.start_new_thread(send, (valveOnDict[int(valveIdx)],)) #threading to increase runtime efficiency
                        currFlipState[valveIdx-1] = '1' #updating flipState
                    elif currFlipState[valveIdx-1] == '1':
                        _thread.start_new_thread(send, (valveOffDict[int(valveIdx)],))
                        currFlipState[valveIdx-1] = '0' #updating flipState
            #print(currFlipState)
            linePrev = line #setting old line value
        end = timer()
        print(end-start)

    btn.config(state='normal') #enabling command button
    btn_text.set("Send Command")

   #previous process command 
def processCommand(btn, btn_text, text, TWindow):
    text = text.strip() #stripping white space
    btn.config(state='disabled') #disabling command button
    btn_text.set("Running Command")
    #data array of all commands
    textData = text.split("\n")
    try:
        #'''
        #running through commands setting all valves listed to closed initally
        for command in textData:
            if command[0] != "V": #making sure syntax is followed
                raise IndexError()
            valveVal = int(command.split("T")[0][1:]) #splitting valve val
            send(valveOnDict[valveVal]) #closing valves initally
        #'''  
        #running through all commands with given time delays
        for command in textData:
            if command[0] != "V": #making sure syntax is followed
                raise IndexError()
            
            valveVal = int(command.split("T")[0][1:]) #splitting valve value
            timeVal = float(command.split("T")[1]) #splitting time value

            send(valveOffDict[valveVal]) #turning valve off, opening
            time.sleep(timeVal) #waiting for close
            send(valveOnDict[valveVal]) #turning valve on after time, closing it

    #exception handeling
    except IndexError:
            btn_text.set("Error")
            messagebox.showinfo("Command Failiure", "Bad command syntax! Refer to help if needed.")
    except ValueError:
            btn_text.set("Error")
            messagebox.showinfo("Command Failiure", "Can only type numeric values! Refer to help if needed.")
    except KeyError:
            btn_text.set("Error")
            messagebox.showinfo("Command Failiure", "Only Valves 1-10 are avalible! Refer to help if needed.")
    #print(text)
    btn.config(state='normal') #enabling command button
    btn_text.set("Send Command")



def updatePressure(label):
    USER_INP = simpledialog.askstring(title="Set Pressure", prompt="Enter Pressure in kPa") #getting user input
    try:
        valP = float(USER_INP) #setting to global pressure var
        stringV.set("Current Pressure " + str(valP) + " kPa")
    except ValueError:
        messagebox.showinfo("Error", "Only numerical values accepted!")

def close():
    MsgBox = messagebox.askquestion ('Exit Application','Are you sure you want to exit the application',icon = 'warning')
    if MsgBox == 'yes':   
        #ser.close()
        root.destroy()
#method for help box        
def helpText():
    messagebox.showinfo("Command Window Help","Type in sequences in the form of X Y where X is the absolute time from 0 when Y should triggered. Y is a binary sequence representing the value of every state. An example of a command would be 0 1111111110, which means at time=0, all the valves are on except the valve 10, which is off. Multiple lines can be entred representing states at differnt times.")
    #messagebox.showinfo("Command Window Help","Type in commands in the form VxTy where x represents the valve number and where y represents the time the valve is open. All valves in the sequence are close intially, opened for the allocated time, then closed at end of allocated time constraint. Add multiple commands by running 1 command per line to run a sequence.")

#method for saving text entries to .txt file
def save_command(TWindow):
    string = TWindow.get("1.0",END)
    fileName = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("text file","*.txt"),("all files","*.*")))
    f = open(fileName+'.txt', "a")
    f.write(string)
    f.close()
    messagebox.showinfo("Saved File", "Commands saved to " + fileName + ".txt")

#mthod to load text from .txt into text window
def load_command(TWindow):
    try:
        fileName = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
        print(fileName)
        f = open(fileName, "r")
        if f.mode == 'r':
            contents = f.read()
            TWindow.delete("1.0", END)
            TWindow.insert(END, contents)
    except FileNotFoundError:
        messagebox.showinfo("Error", "File not found!")

    
def sequence1(btn, btn_text, e1, e2, e3):
    btn.config(state='disabled') #disabling command button
    btn_text.set("Running Sequence")
    try:
        e1_num = float(e1)
        e2_num = float(e2)
        e3_num = float(e3)

        #certain sequence of commands
        send(valveOnDict[1])
        send(valveOnDict[2])
        send(valveOnDict[7])
        time.sleep(e1_num)
        send(valveOffDict[1])
        send(valveOffDict[2])
        send(valveOffDict[7])

        send(valveOnDict[5])
        send(valveOnDict[6])
        send(valveOnDict[9])
        send(valveOnDict[10])
        time.sleep(e2_num)
        send(valveOffDict[5])
        send(valveOffDict[6])
        send(valveOffDict[9])
        send(valveOffDict[10])

        send(valveOnDict[3])
        send(valveOnDict[4])
        send(valveOnDict[9])
        send(valveOnDict[10])
        time.sleep(e3_num)
        send(valveOffDict[3])
        send(valveOffDict[4])
        send(valveOffDict[9])
        send(valveOffDict[10])        

    except ValueError:
            btn_text.set("Error")
            messagebox.showinfo("Command Failiure", "Can only type numeric values!")
        
    btn.config(state='normal') #enabling command button
    btn_text.set("Run Sequence 1")

def sequence2(btn, btn_text, e4, e5, e6):
    btn.config(state='disabled') #disabling command button
    btn_text.set("Running Sequence")
    try:
        e4_num = float(e4)
        e5_num = float(e5)
        e6_num = float(e6)

        #certian sequence of commands
        send(valveOnDict[1])
        send(valveOnDict[2])
        send(valveOnDict[7])
        time.sleep(e4_num)
        send(valveOffDict[1])
        send(valveOffDict[2])
        send(valveOffDict[7])

        send(valveOnDict[5])
        send(valveOnDict[6])
        send(valveOnDict[7])
        time.sleep(e5_num)
        send(valveOffDict[5])
        send(valveOffDict[6])
        send(valveOffDict[7])

        send(valveOnDict[3])
        send(valveOnDict[4])
        send(valveOnDict[9])
        send(valveOnDict[10])
        time.sleep(e6_num)
        send(valveOffDict[3])
        send(valveOffDict[4])
        send(valveOffDict[9])
        send(valveOffDict[10])        

    except ValueError:
            btn_text.set("Error")
            messagebox.showinfo("Command Failiure", "Can only type numeric values!")
        
    btn.config(state='normal') #enabling command button
    btn_text.set("Run Sequence 2")

#setup for sequences window
def sequence_setup():
    root2 = Toplevel()
    subFrameTopRight = Frame(root2, width = 474, height = 450, bg = 'white')
    subFrameTopRight.pack(side=TOP)
    subFrameTopRight.pack_propagate(0)

    l1 = Label(subFrameTopRight, text = "Sequence 1", bg = 'white')
    l1.config(font=(14))
    l1.grid(row = 0, column = 0, columnspan = 2)

    Label(subFrameTopRight, text = "Time Between Valve 1-2 Open and Waste Valve 7 Close     ", bg = 'white').grid(row=1, column=0)
    e1 = Entry(subFrameTopRight)
    e1.grid(row = 1, column = 1)

    Label(subFrameTopRight, text = "Time Between Flushing Valves 5-6 and Opening Valves 9-10", bg = 'white').grid(row=2, column=0)
    e2 = Entry(subFrameTopRight)
    e2.grid(row = 2, column = 1)

    Label(subFrameTopRight, text = "Time Between Flushing Valves 3-4 and Opening Valves 9-10", bg = 'white').grid(row=3, column=0)
    e3 = Entry(subFrameTopRight)
    e3.grid(row = 3, column = 1)

    btn_text_seq1 = StringVar()
    btn_text_seq1.set("Run Sequence 1")
    sendSeq1 = Button(subFrameTopRight, relief=GROOVE, textvariable=btn_text_seq1,command = lambda:_thread.start_new_thread(sequence1,(sendSeq1, btn_text_seq1, e1.get(), e2.get(), e3.get()))) #add menu bar with 'help' that shows command syntax
    sendSeq1.grid(row = 4, column = 0, columnspan = 2)

    Label(subFrameTopRight, text = "", bg = 'white').grid(row = 5, column = 0, columnspan = 2)

    l2 = Label(subFrameTopRight, text = "Sequence 2", bg = 'white')
    l2.config(font=(14))
    l2.grid(row = 6, column = 0, columnspan = 2)

    Label(subFrameTopRight, text = "Time Between Valve 1-2 Open and Waste Valve 7 Close", bg = 'white').grid(row=7, column=0)
    e4 = Entry(subFrameTopRight)
    e4.grid(row=7, column = 1)

    Label(subFrameTopRight, text = "Time Between Valve 5-6 Open and Waste Valve 7 Close", bg = 'white').grid(row=8, column=0)
    e5 = Entry(subFrameTopRight)
    e5.grid(row=8, column = 1)

    Label(subFrameTopRight, text = "Time Between Valve 3-4 Open and Opening Valves 9-10", bg = 'white').grid(row=9, column=0)
    e6 = Entry(subFrameTopRight)
    e6.grid(row=9, column = 1)

    btn_text_seq2 = StringVar()
    btn_text_seq2.set("Run Sequence 2")
    sendSeq2 = Button(subFrameTopRight, relief=GROOVE, text="Test",textvariable=btn_text_seq2, command = lambda:_thread.start_new_thread(sequence2,(sendSeq2, btn_text_seq2, e4.get(), e5.get(), e6.get()))) #add menu bar with 'help' that shows command syntax
    sendSeq2.grid(row = 10, column = 0, columnspan = 2)
    
    root2.mainloop()
def set_default_state():
    send(valveOnDict[8])
    send(valveOnDict[1])
    send(valveOffDict[2])
    send(valveOffDict[7])
    send(valveOffDict[9])
    send(valveOnDict[10])
    send(valveOffDict[6])
    send(valveOffDict[5])
    send(valveOffDict[4])
    send(valveOffDict[3])

def inject(btn, btn_text):
    btn.config(state='disabled')
    btn_text.set("Running")
    try:
        set_default_state()
        send(valveOnDict[8])
        send(valveOffDict[1])
        send(valveOnDict[2])
        #time.sleep(timeVal)
        messagebox.showinfo("Injected Sample", "Press OK when sample discretization is complete.")
        send(valveOffDict[2])
        send(valveOnDict[1])
        send(valveOffDict[8])
    except ValueError:
        btn_text.set("Error")
        messagebox.showinfo("Command Failiure", "Can only type numeric values!")

    btn.config(state='normal') #enabling command button
    btn_text.set("Slug Generation")

def release_samples(releaseNum, btn, btn_text,c1,c2,c3,c4):
    btn.config(state='disabled')
    if releaseNum.get() == 1:
        if(c1 == 1):
            release_yes(6)

        else:
            release_no(6)
        releaseNum.set(2) #incrementing num
        btn_text.set("Release Droplet 5")

    elif releaseNum.get() == 2:
        if(c2 == 1):
            release_yes(5)
        else:
            release_no(5)
        releaseNum.set(3) #incrementing num
        btn_text.set("Release Droplet 4")

    elif releaseNum.get() == 3:
        if(c3 == 1):
            release_yes(4)
        else:
            release_no(4)
        releaseNum.set(4) #incrementing num
        btn_text.set("Release Droplet 3")

    elif releaseNum.get() == 4:
        if(c4 == 1):
            release_yes(3)
        else:
            release_no(3)
        releaseNum.set(1) #resetting num
        messagebox.showinfo("Droplet Released", "All Droplets Released. Press OK to reset valves to default states") #message showing what happened
        set_default_state()
        btn_text.set("Release Droplet 6")
    btn.config(state='normal')

    
#helper methods to relase dropletts 
def release_yes(valve):
    send(valveOnDict[valve])
    send(valveOnDict[7])
    send(valveOffDict[8])
    messagebox.showinfo("Droplet Released", "Released droplet %s. Transferring to merging" % valve) #message showing what happened


def release_no(valve):
    send(valveOnDict[valve])
    send(valveOffDict[7])
    send(valveOnDict[8])
    messagebox.showinfo("Droplet Released", "Released droplet %s. Transferring to waste" % valve) #message showing what happened

def launch(var, btn):
    btn.config(state='disabled')
    var.set("Releasing...")
    send(valveOnDict[8])
    send(valveOffDict[10])
    time.sleep(1) #added delay to make sure there is time
    send(valveOnDict[7])
    time.sleep(1)
    send(valveOnDict[9])
    time.sleep(1)
    messagebox.showinfo("Merged Droplet Release", "Merged droplets were released. Press OK to reset valves to default states")
    set_default_state()
    btn.config(state='normal')
    var.set("Release Merged Droplets")

def default_setup():
    os.system('python setupGUI.py')
    MsgBox = messagebox.askquestion ('Restart Application','Do you want to apply new changes now?',icon = 'warning')
    if MsgBox == "yes":
        close()
#root setup
root.title("Valve Toggler")
root.geometry("1084x554")
root.resizable(0,0)
root.configure(background='white')
root.protocol("WM_DELETE_WINDOW", close)

#top frame setup
topFrame = Frame(root, width=1084, height=30)
topFrame.pack(side=TOP)
topFrame.grid_propagate(0)

#left frame setup
leftFrame = Frame(root, width=410, height=474)
leftFrame.pack(side=LEFT)

#right frame setup
rightFrame = Frame(root, width=674, height=474)
rightFrame.pack(side=RIGHT)

#Menu bar setup
menubar = Menu(root)
filemenu = Menu(menubar)
filemenu.add_command(label="Save Command Data", command=lambda:save_command(TWindow))
filemenu.add_command(label="Load Command Data", command=lambda:load_command(TWindow))
menubar.add_cascade(label="File", menu=filemenu)
menubar.add_command(label="Help", command=helpText)
menubar.add_command(label="Run Sequences", command=sequence_setup)
menubar.add_command(label="Setup New Experiment",command=lambda:default_setup())
menubar.add_command(label="Exit", command=lambda:close())
root.config(menu=menubar)


#Image Placement
C = Canvas(leftFrame, bg="white", height=474, width=400)

img = PIL.Image.open(LD_filename)
img = img.resize((400,474),PIL.Image.ANTIALIAS)
#filename = PhotoImage(file = LD_filename)
filename = ImageTk.PhotoImage(img)

background_label = Label(leftFrame, image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
C.pack()

#Top Frame Content
subFrame1 = Frame(topFrame, width=410,height=30, bg = 'white')
labelTopL = Label(subFrame1, text = "Manual Control", bg="white")
labelTopL.config(font=(20))
labelTopL.place(relx=.5, rely=.5, anchor="center")
subFrame1.pack(side=LEFT)

subFrame2 = Frame(topFrame, width=674,height=30, bg = 'white')
labelTopR = Label(subFrame2, text = "Automatic Control", bg = 'white')
labelTopR.config(font=(20))
labelTopR.place(relx=.5, rely=.5, anchor="center")
subFrame2.pack(side=RIGHT)

#Right Frame Content
subFrameTop = Frame(rightFrame, width=674, height = 450, bg = 'white')
subFrameTop.pack(side=TOP)
subFrameTop.pack_propagate(0)

#runs on new thread
#sendDat = Button(subFrameTop, text = "Send Command",command = lambda:processCommand(TWindow.get("1.0",END), TWindow)) #add menu bar with 'help' that shows command syntax

btn_text = StringVar()
btn_text.set("Send Command")
subFrameTopLeft = Frame(subFrameTop, width = 200, height = 450)
subFrameTopLeft.pack(side=LEFT)
subFrameTopLeft.pack_propagate(0)

sendDat = Button(subFrameTopLeft, relief=GROOVE,  textvariable=btn_text,command = lambda:_thread.start_new_thread(processCommand2,(sendDat, btn_text, TWindow.get("1.0",END), TWindow))) #add menu bar with 'help' that shows command syntax
sendDat.pack(side=BOTTOM, fill = X)

S = Scrollbar(subFrameTopLeft)
TWindow = Text(subFrameTopLeft)
S.pack(side=RIGHT, fill=Y)
TWindow.pack(side=LEFT,fill=Y)
S.config(command=TWindow.yview)
TWindow.config(yscrollcommand=S.set)
#-------------------------
subFrameTopRight = Frame(subFrameTop, width = 474, height = 450, bg = 'white')
subFrameTopRight.pack(side=TOP)
subFrameTopRight.pack_propagate(0)
#-------Default Values-----------
#NOT WORKING RIGHT NOW, NOT CRITICAL TO PROGRAM
#Note: issue with mainloop(), breaking send function while all other send() calls within method
#root.after(500, set_default_state) #setting valves to default values
tempVar = IntVar()
tempB = Radiobutton(root, variable=tempVar, command=lambda:_thread.start_new_thread(set_defualt_state, ()))
tempB2 = Radiobutton(root, variable=tempVar, command=lambda:_thread.start_new_thread(set_defualt_state, ()))
tempVar.set(1);

#--------------------------------

l1 = Label(subFrameTopRight, text = "Sample Injection and Discritization", bg = 'white')
l1.config(font=(14))
l1.grid(row=0, column=0, columnspan = 2)
#Label(subFrameTopRight, text="Time between sample injection start and end:    ", bg = 'white').grid(row=1, column=0)
#e1 = Entry(subFrameTopRight)
#e1.grid(row=1, column=1)
btn_text_inject = StringVar()
btn_text_inject.set("Slug Generation")
injectBtn = Button(subFrameTopRight, relief=GROOVE, textvariable=btn_text_inject, command=lambda:_thread.start_new_thread(inject, (injectBtn, btn_text_inject)))
injectBtn.grid(row=2, column = 0, columnspan = 2)
Label(subFrameTopRight, bg='white').grid(row=3)

l2 = Label(subFrameTopRight, text = "Select Desired Droplets", bg = 'white')
l2.config(font=(14))
l2.grid(row=4, column=0, columnspan = 2)

cBoxFrame = Frame(subFrameTopRight, bg = 'white')
cBoxFrame.grid(row=5, column=0, columnspan=4)
Label(cBoxFrame,text="Valve 6", bg = 'white').grid(row=5, column=0)
Label(cBoxFrame,text="Valve 5", bg = 'white').grid(row=5, column=2)
Label(cBoxFrame,text="Valve 4", bg = 'white').grid(row=5, column=4)
Label(cBoxFrame,text="Valve 3", bg = 'white').grid(row=5, column=6)

c1_val = IntVar()
c1 = Checkbutton(cBoxFrame, variable = c1_val,  bg='white')
c1.grid(row=6, column=0)
c2_val = IntVar()
Label(cBoxFrame, text="\t", bg='white').grid(row=6, column=1)
c2 = Checkbutton(cBoxFrame, variable = c2_val,  bg='white')
c2.grid(row=6, column=2)
Label(cBoxFrame, text="\t", bg='white').grid(row=6, column=3)
c3_val = IntVar()
c3 = Checkbutton(cBoxFrame, variable = c3_val,  bg='white')
c3.grid(row=6, column=4)
Label(cBoxFrame, text="\t", bg='white').grid(row=6, column=5)
c4_val = IntVar()
c4 = Checkbutton(cBoxFrame, variable = c4_val,  bg='white')
c4.grid(row=6, column=6)

btn_text_release = StringVar()
btn_text_release.set("Release Droplet 6")
releaseBtn = Button(subFrameTopRight, relief=GROOVE, textvariable=btn_text_release, command=lambda:_thread.start_new_thread(release_samples, (releaseNum, releaseBtn, btn_text_release,c1_val.get(),c2_val.get(),c3_val.get(),c4_val.get())))
releaseBtn.grid(row=6, column=0, columnspan=2)
releaseNum = IntVar()
releaseNum.set(1)
Label(subFrameTopRight, bg='white').grid(row=7)

l3 = Label(subFrameTopRight, text = "Release Selected Droplets", bg = 'white')
l3.config(font=(14))
l3.grid(row=8, column=0, columnspan = 2)
text_final = StringVar()
text_final.set("Release Merged Droplets")
finalButton = Button(subFrameTopRight, relief=GROOVE, textvariable=text_final, command=lambda:_thread.start_new_thread(launch, (text_final, finalButton)))
finalButton.grid(row=9, column=0, columnspan=2)
Label(subFrameTopRight, text='', bg='white').grid(row=10, column=0)


'''

    Label(subFrameTopRight, text = "Time Between Flushing Valves 3-4 and Opening Valves 9-10", bg = 'white').grid(row=3, column=0)
    e3 = Entry(subFrameTopRight)
    e3.grid(row = 3, column = 1)

    btn_text_seq1 = StringVar()
    btn_text_seq1.set("Run Sequence 1")
    sendSeq1 = Button(subFrameTopRight, relief=GROOVE, textvariable=btn_text_seq1,command = lambda:_thread.start_new_thread(sequence1,(sendSeq1, btn_text_seq1, e1.get(), e2.get(), e3.get()))) #add menu bar with 'help' that shows command syntax
    sendSeq1.grid(row = 4, column = 0, columnspan = 2)
'''

#-------------------------
subFrameBot = Frame(rightFrame, width=674, height = 24)
subFrameBot.pack(side=BOTTOM)

stringV = StringVar()
stringV.set("Current Pressure " + str(valP) + " kPa")
pLabel = Label(subFrameBot,textvariable = stringV, width = 50, bg = 'white')
setP = Button(subFrameBot, relief=GROOVE, text = "Set Pressure", width = 30,command = lambda:updatePressure(valP))
exitB =Button(subFrameBot, relief=GROOVE, text = "Exit", width = 12, command = lambda:close())
pLabel.grid(row = 0, column = 0, sticky=E)
setP.grid(row = 0, column = 1)
exitB.grid(row = 0, column = 2, sticky=W)

#Radio Buttons for leftFrame

frameList = []
for i in range(0,numValves):
    frameT = Frame(leftFrame, highlightbackground="#5AE652", highlightcolor="#5AE652", highlightthickness=1)
    von = valveOnDict[i+1]
    voff = valveOffDict[i+1]
    BO =  Radiobutton(frameT,text="On", variable = varList[i], value = 1, indicatoron = 0, bg = 'white', command =partial(send,von)) #using partial bc lambda fucntion doesnt work well in loops
    BF = Radiobutton(frameT,text="Off", variable = varList[i], value = 0, indicatoron  = 0, bg = 'white', command =partial(send,voff))
    labelTemp = Label(frameT,text = "Valve %d" % (i+1), bg = 'gray99')
    
    labelTemp.pack(side=TOP, fill=X)
    BO.pack(side=LEFT)
    BF.pack(side=RIGHT)
    frameT.place(x=varLocations[i][0], y=varLocations[i][1], in_=leftFrame)
    frameList.append(frameT)

root.mainloop()


