# kami2
### 项目描述
使用pyside6编写的神折纸2复刻项目，最初只是为了展示训练好的模型玩游戏的效果，也就是旅程关卡中的提示部分，所以一开始只是想使用pygame做一个小demo的。      
后来跟朋友提起，她说期待一下，我想样子还是不能太寒碜，就学了pyside6去整饬下样子。      
她玩了觉得挺有意思，说后面的关卡，看了提示才知道原来要这样弄。我觉得既高兴又有点遗憾，高兴在于我弄一些东西出来的时候她总是愿意去试，遗憾的是很难进行更深入的交流。  
像提示我其实提过花了很多时间去训练模型，她对此的感觉就是不明觉厉，但是没办法更深入的交流，我不可能让她也去学点深度强化学习，对吧？     
模型的训练参考我的另一个项目：[ddqn-kami2](https://github.com/laidage/ddqn-kami2)    

### 如何运行
你可以下载打包好的[windows安装包](https://github.com/laidage/kami2/releases/download/v1.0.0/kami2.zip)，解压后打开kami2.exe，即可运行。  
或者按以下步骤使用源码运行：  
你可以创建一个干净的python虚拟环境(适用于python3.3以上版本)   
`python -m venv $虚拟环境目录`   
激活虚拟环境   
linux环境：  
`$虚拟环境目录/bin/activate`   
windwos环境：  
`cd $虚拟环境目录/`  
`Scripts/activate`  
在虚拟环境中切换到项目目录下  
`cd $项目目录`  
安装依赖   
`pip install -r requirements.txt`   
运行游戏   
`python kami2.py`   