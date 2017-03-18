import pickle
import os

class Transitions:
    def __init__(self,prevState,prevAction,state,last=False):
        self.s0 = prevState
        self.a0 = prevAction
        self.s1 = state
        self.r1 = 0 if not last else -1

        
c = 0
for fn in os.listdir("transitions"):
	with open("./transitions/"+fn,'rb') as file:
		trans = pickle.load(file)
		c += len(trans)

print(c)