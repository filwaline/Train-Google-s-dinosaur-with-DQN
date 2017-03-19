import numpy as np
from itertools import chain

class DeepQLearningBrain:
	def __init__(self,networkDefine,option):
		self.discount = option.get("discount", 0.7)
		# self.temporalWindow = option.get("temporalWindow", 3)
		self.experienceSize = option.get("experienceSize", 30000)
		self.startLearningThreshold = option.get("startLearningThreshold",1000)
		self.explorationMode = option.get("mode", "epsilon") # ε-greedy method or softmax action selection

		if self.explorationMode == "softmax":
			self.temperature = option.get("temperature", 0.1)    
			def softmax(values,t):
				overall = sum(np.exp(v/t) for v in values)
				possibilityInterval = [0]
				for v in values:
					possibilityInterval.append(np.exp(v/t)/overall + possibilityInterval[-1])
				theSoftmaxChoice = bisect(possibilityInterval[1:],np.random.random())
				return theSoftmaxChoice,np.exp(values[theSoftmaxChoice]/t)/overall
			self.softmaxFunc = softmax

		elif self.explorationMode == "epsilon":
			self.epsilon = 1.0                                     	# 初始探索率
			self.minEpsilon = option.get("minEpsilon", 0.1)        	# 最小探索率
			self.randomStartup = option.get('randomStartup', 2000) 	# 初始完全随机的步数
			self.stepsUntilReachMinEpsilon = option.get('stepsUntilReachMinEpsilon',20000) # 降到最低探索率所需步数
			# self.decayRate = option.get('decayRate', 0.95)        # 随机探索衰减率
			self.distribution = option.get('distribution', None)    # 选择action的概率分布，默认为均等分布
		else:
			raise RuntimeError()
		
		self.age = 0
		self.policyNetwork = networkDefine()
		self.valueNetwork = networkDefine()
		self.batch_size = 2
		self.experiences = []
		self.actionMap = {'Space':0,'Up':0,'Down':1,None:2}


	def forward(self,state):
		if state is None:
			return np.random.choice([0,1,2])
		elif state.shape != (30,150,4):
			raise RuntimeError()

		Qvalue = self.model.predict(state,verbose=0)

		if self.explorationMode == 'epsilon':
			self.epsilon = max(self.minEpsilon,min(1.0,1.0-(self.age - self.randomStartup)/(self.stepsUntilReachMinEpsilon - self.randomStartup)))
			if np.random.random() < self.epsilon:
				action = np.random.choice([0,1,2],p=self.distribution)
			else:
				action = np.argmax(Qvalue,axis=1)
		else: # softmax mode
			action,possibility = self.softmaxFunc(Qvalue,self.temperature)
		
		# self.lastAction = action
		return action

	def backward(self):
		randomIndex = np.random.choice(np.arange(len(self.experiences)),self.batch_size)
		non_terminal_trans = [self.experiences[ri] for ri in randomIndex if self.experiences[ri].s1 is not None]
		terminal_trans = [self.experiences[ri] for ri in randomIndex if self.experiences[ri].s1 is None]

		minibatch_S0 = np.stack([t.s0 for t in chain(non_terminal_trans,terminal_trans)],axis=0)
		minibatch_S1 = np.stack([t.s1 for t in non_terminal_trans],axis=0)
		minibatch_R1 = np.array([t.r1 for t in non_terminal_trans])

		origin = self.policyNetwork.predict_on_batch(minibatch_S0)
		value = self.valueNetwork.predict_on_batch(minibatch_S1)
		maxValue = np.max(value,axis=1)
		target = minibatch_R1 + self.discount * maxValue

		if terminal_trans:
			target = np.append(target,[t.r1 for t in terminal_trans])

		y = origin
		for i,ri in enumerate(randomIndex):
			action = self.experiences[ri].a0
			ac = self.actionMap[action]
			y[i,ac] = target[i]

		self.policyNetwork.train_on_batch(minibatch_S0,y)


	def learn(self,transitionsGen):

		for trans in transitionsGen:
			self.age += 1

			if len(self.experiences) < self.experienceSize:
				self.experiences.append(trans)
			else:
				self.experiences[np.random.randint(0,self.experienceSize)] = trans
			
			if self.age > self.startLearningThreshold:
				self.backward()

				# update value network 
				if self.age % 1200 == 0:
					weights = self.policyNetwork.get_weights()
					self.valueNetwork.set_weights(weights)

				if self.age % 1500 == 0:
					self.policyNetwork.save_weights('model\\policy.h5')
					self.valueNetwork.save_weights('model\\value.h5')
					print(self.age)


