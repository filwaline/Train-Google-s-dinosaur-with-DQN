
# coding: utf-8

# In[1]:

from PIL import Image,ImageGrab
from gameoverCLF import GameOverCLF

import win32api
import win32con
import pythoncom
import pyHook
import pickle
import os
import threading
import time
import numpy as np


# In[2]:

bbox = [660,126,1260,276]
currentKeyPress = None
hookThreadID = None
stopListen = False
startCaptureFlag = False
resetFlag = True
breakFlag = False
focusFlag = False
lock = threading.Lock()


# In[4]:

def captureMainFunc():
    
    def mainloop(goc):
        global resetFlag, startCaptureFlag
        while True:
            if not resetFlag:
                continue

            roundCapture(goc)

            lock.acquire()
            resetFlag = False
            startCaptureFlag = False
            lock.release()

            if breakFlag:
                break
        print("end of capture!")
        
    def roundCapture(goc):
        pixels = []
        actions = []

        while True:
            if startCaptureFlag:
                break
        
        time.sleep(3.5)
        start = time.time()
        while True:
            if not focusFlag:
                continue

            actions.append(currentKeyPress)
            rawPixels = ImageGrab.grab(bbox)
            pixels.append(np.array(rawPixels))
            
            if len(actions) % 100 == 0:
                print("{} frames had captured.".format(len(actions)))
                print("average {} frames per second.".format(len(actions)/(time.time()-start)))
            if goc.isGameOver(rawPixels):
                print("Game Over.")
                print("{} frames had captured.".format(len(actions)))
                print("average {} frames per second.".format(len(actions)/(time.time()-start)))
                print("Press F5 to reset game, and then Press Space to restart.")
                print("Or you may press Esc to stop.")
                break

            if breakFlag:
                return

        code = len(os.listdir(".\\human"))
        with open(".\\human\\human_{:0>4d}.p".format(code),"wb") as f:
            pickle.dump([pixels,actions],f)
            print("save at .\\human\\human_{:0>4d}.p".format(code))
            
    goc = GameOverCLF()
    mainloop(goc)


# In[5]:

def hookMainFunc():
    def OnKeyDownEvent(event):
        global currentKeyPress,startCaptureFlag,resetFlag,focusFlag
        
        if event.WindowName == "index.html - Google Chrome":
            focusFlag = True
            
            if event.Key == 'F5':
                resetFlag = True
                print("Reset Done. Ready to Next Round.")
                
            if event.Key == 'Space' and not startCaptureFlag:
                if resetFlag:
                    print("Start record game play.")
                    startCaptureFlag = True
                else:
                    print("Can't record game until you reset it, press F5 please.")
            
            currentKeyPress = event.Key
            if event.Key not in ['Space','Up','Down']:
                currentKeyPress = None
        else:
            print("lost focus, can't not record.")
            focusFlag = False
            currentKeyPress = None
        print("press down: {:>5s}".format(event.Key))

        return True 
    
    def OnKeyUpEvent(event):
        global currentKeyPress
        if event.WindowName == "index.html - Google Chrome": 
            if currentKeyPress == event.Key:
                currentKeyPress = None
            if event.Key not in ['Space','Up','Down']:
                currentKeyPress = None
        else:
            currentKeyPress = None
        
        if event.Key == "Escape":
            global breakFlag
            breakFlag = True
            lock.acquire()
            hm.UnhookKeyBoard()
            lock.release()
            
        print("release: {:>5s}".format(event.Key))
        return True
    
    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyDownEvent
    hm.KeyUp = OnKeyUpEvent
    hm.HookKeyboard()
    pythoncom.PumpMessages()



# In[6]:

t1 = threading.Thread(target=captureMainFunc)
t2 = threading.Thread(target=hookMainFunc)

t1.start()
t2.start()


