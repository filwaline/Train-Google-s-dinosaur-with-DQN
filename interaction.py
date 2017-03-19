import win32api,win32con,win32gui,win32com.client
import time,sys
import msvcrt

VK_CODE = {'Up':0x26,'Down':0x28,'Enter':0x0D,'Space':0x32,'F5':0x74}

def hitKey(key,t):
	if key is None:
		return
	k = VK_CODE[key]
	win32api.keybd_event(k,0,0,0)
	time.sleep(t)
	win32api.keybd_event(k,0,win32con.KEYEVENTF_KEYUP,0)

def releaseKey(lastHoldKey):
	if lastHoldKey is None:
		return
	key = VK_CODE[lastHoldKey]
	win32api.keybd_event(key,0,win32con.KEYEVENTF_KEYUP,0)

def pushDownKey(action):
	if action is None:
		return
	key = VK_CODE[action]
	win32api.keybd_event(key,0,0,0)

def foucsWindowSwitchHandler(hwnd, names):
	if win32gui.IsWindowVisible(hwnd):
		if any(part in win32gui.GetWindowText(hwnd) for part in names):
			##### 
			# prevent switch error 
			# http://stackoverflow.com/questions/14295337/win32gui-setactivewindow-error-the-specified-procedure-could-not-be-found
			shell = win32com.client.Dispatch("WScript.Shell")
			shell.SendKeys('%')
			#####
			win32gui.SetForegroundWindow(hwnd)
			return # first only

def foucsWindowHandler(hwnd, names):
	if win32gui.IsWindowVisible(hwnd):
		if any(part in win32gui.GetWindowText(hwnd) for part in names):
			win32gui.SetForegroundWindow(hwnd)
			return # first only

def focusWindow(*names,switch=True):
	if switch:
		win32gui.EnumWindows(foucsWindowSwitchHandler, names)
	else:
		win32gui.EnumWindows(foucsWindowHandler, names)

def pauseUntilReady(string,code=32,wrongMsg='hit space bar please!',exitCode=b'\x03'):
	print(string)
	while True:
		if ord(msvcrt.getch()) == code:
			break
		if msvcrt.getch() == exitCode:
			sys.exit('stop by hand.')
		print(wrongMsg)

