## 第十六届全国大学生智能汽车竞赛-讯飞创意组（ROS）

Ubuntu18.04 & ROS melodic



### 1. 将路径添加到source中

打开终端输入如下指令

```bash
sudo gedit ~/.bashrc //若没有安装gedit，则使用install指令安装
```

下拉文件至末查看是否有如下路径

```bash
source ~/gazebo_test_ws/devel/setup.bash
```

- 若不存在，输入如下指令：

```bash
echo "source ~/gazebo_test_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc //使配置的环境变量生效
```



### 2. 安装move_base

```bash
sudo apt install ros-melodic-navigation*
```



### 3. 安装teb_local_planner

```bash
sudo apt-get install ros-melodic-teb-local-planner
```



### 4.  运行模板程序

在gazebo_test_ws/src/start_game目录下，运行main.py 

```bash
cd ~/gazebo_test_ws/src/start_game
python2 main.py
```

右键main.py - Properties - Permissions 

勾上Execute: Allow executling file as program
