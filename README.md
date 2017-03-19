# Train-Google-s-dinosaur-with-DQN
使用Deep Q Learning训练Google Chrome离线小恐龙。

参考资料：
+ [DQN 从入门到放弃](https://zhuanlan.zhihu.com/p/21262246)
+ [Guest Post (Part I): Demystifying Deep Reinforcement Learning](https://www.nervanasys.com/demystifying-deep-reinforcement-learning/)
+ [Reinforcement Learning: An Introduction - Sutton](http://people.inf.elte.hu/lorincz/Files/RL_2006/SuttonBook.pdf)
+ [UCL Reinforcement Learning Lecture - David Silver](http://www0.cs.ucl.ac.uk/staff/d.silver/web/Teaching.html)

## game play
包含了用于获取人类游戏数据的脚本。

+ count.py
  - 获取**transition**的总数
+ capture.py
  - PIL 截取屏幕（仅windows可用）
  - pyHook 监控按键
  - pickle 将数据序列化
  - 数据存储在 `./game play/human/`
+ gameoverCLF.py
  - 用于判断截屏是不是game over
  - 使用 Keras 2.0 API 
  - h5 文件位于 `./game play/clf/`
+ analyze.ipynb
  - 提供简易分析，检查capture是否符合DQN的要求
+ preprocess.ipynb
  - 对截屏进行预处理，转化成可供DQN直接学习的transition
  - 从`./game play/human/`提取文件，处理完毕后，存储在`./game play/transitions/`

## deepQnetwork.py
Deep Q Learning的架构，不包括神经网络定义

需要从外部传入神经网络定义，和其他一些参数

### 对象方法
+ learn(self,transGen)
  - 从已有的transitions中学习，需要传入生成器
  - 把从生成器中获取的trans存入经验池experiences，随机生成minibatch，反复调用backward进行学习
+ backward(self)
  - 目标函数是最小化 predict_Q 与 reward + future_maxQ 的差
  - 遇到terminal state时不计算future_maxQ
+ forward(self,state)
  - state 要经过预处理，大小应为（30,150,4）
  - 探索模式分 ε-greedy method 和 softmax action selection
  - softmax 参数不好调，不建议使用

### 参数说明
+ discount
  - gamma，或折现率
+ experienceSize
  - 经验池的最大容量
+ startLearningThreshold
  - 经验池存储多少样本后才开始学习
+ explorationMode
  - ε-greedy method
  - softmax action selection
+ temperature
  - softmax 参数
  - https://en.wikipedia.org/wiki/Softmax_function
+ minEpsilon
  - ε-greedy method 参数
  - 最小探索率
+ randomStartup
  - ε-greedy method 参数
  - 初始完全随机的步数
+ stepsUntilReachMinEpsilon
  - ε-greedy method 参数
  - 降到最低探索率所需步数
+ distribution
  - ε-greedy method 参数
  - 选择action的概率分布，默认为均等分布
  
## interaction.py
实现与windows系统的交互，窗口聚焦，模拟按键
