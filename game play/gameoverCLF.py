from keras.models import load_model
from keras.utils.np_utils import normalize
import numpy as np
import cv2

class GameOverCLF:
	def __init__(self):
		self.model = load_model("clf\\gameoverCLF.h5")

	def isGameOver(self,rawPixels):
		signalEncode = self.signalEncoder(rawPixels)
		cut = signalEncode[:,40:80,:]
		flatten = normalize(cut.reshape((1,1200)))
		if self.model.predict_classes(flatten,verbose=0) == 0:
			print('game over!')
			return True
		return False

	def signalEncoder(self, rawPixels):
		npimg = np.array(rawPixels)
		gray = cv2.cvtColor(npimg,cv2.COLOR_BGR2GRAY)
		scoreRegion = gray[0:30,430:] #(y,x)
		vertices = np.array([[(430,30),(430,0),(600,0),(600,30)]]) 
		regionFill = cv2.fillPoly(np.copy(gray),vertices,(255))
		visionEncode = cv2.resize(regionFill,(120,30),interpolation=cv2.INTER_AREA) 
		signalEncode = visionEncode[:,:,None] # (row,col) -> (row,col,1)
		return signalEncode