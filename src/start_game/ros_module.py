#! /usr/bin/env python2
# -*- coding: utf-8 -*-


import time
import json
import rospy
import actionlib
from geometry_msgs.msg import Twist, Vector3
from rosgraph_msgs.msg import Clock
from nav_msgs.msg import Odometry
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

class ROSNavNode(object):

    def __init__(self):
        rospy.init_node('test')
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.odom_subsciber = rospy.Subscriber("/odom", Odometry, self._get_info)
        self.time_subsciber = rospy.Subscriber("/clock", Clock, self._get_cur_time)

        self.info = Odometry()
        self.pos_diff = 10.0
        self.last_pose = Vector3()
        self.last_pose.x = 0.0
        self.last_pose.y = 0.0
        self.curr_time = 0.0
        
        # 一定要有这一行，读 actionlib 源码可以看到 client 和 server 会在建立连接时进行协商，然后丢掉第一个 goal
        # http://docs.ros.org/en/jade/api/actionlib/html/action__client_8py_source.html
        self.client.wait_for_server()
        
        self._get_pose()

    def _get_info(self, msg):
        '''
        获取gazebo中odometry
        '''
        self.info = msg
        
        self.pos_diff = abs(self.last_pose.x - self.info.pose.pose.position.x) + abs(self.last_pose.y - self.info.pose.pose.position.y)
        
        self.last_pose.x = self.info.pose.pose.position.x
        self.last_pose.y = self.info.pose.pose.position.y

    def _get_cur_time(self, msg):
        '''
        获取sim time
        '''
        self.curr_time = msg.clock
        
        
    
    def _get_pose(self):
        '''
        从文件中读取目标点位置
        '''
        with open('pose.json', 'r') as f:
            text = json.loads(f.read())
            self.pos_x = text['position']['x']
            self.pos_y = text['position']['y']
            self.pos_z = text['position']['z']
            self.ori_x = text['orientation']['x']
            self.ori_y = text['orientation']['y']
            self.ori_z = text['orientation']['z']
            self.ori_w = text['orientation']['w']
        

    def _goal_pose(self):
        '''
        构造 goal
        '''
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = 'map'
        self.goal.target_pose.pose.position.x = self.pos_x
        self.goal.target_pose.pose.position.y = self.pos_y
        self.goal.target_pose.pose.position.z = self.pos_z
        self.goal.target_pose.pose.orientation.x = self.ori_x
        self.goal.target_pose.pose.orientation.y = self.ori_y
        self.goal.target_pose.pose.orientation.z = self.ori_z
        self.goal.target_pose.pose.orientation.w = self.ori_w
    
    def send_goal(self):
        '''
        发送 goal
        '''
        self._goal_pose()
        self.client.send_goal(self.goal)

    ## 车模停止且小车在终点图内，目标完成，停止计时
    ## 停止条件：cmd_vel < 0.2 or 0.2秒内position变化小于一个值
    def get_state(self):
        '''
        判断目标完成情况，若完成目标则返回 True
        '''
        # self.client.get_state()
        # 这里其实调用 actionlib 库提供的 get_state() 方法效率更高，但是返回的貌似是 int 
        # 我懒得读源码里 Magic Number 具体代表哪一种状态了，所以直接调用下面返回字符串的方法
        # if self.client.get_goal_status_text() == 'Goal reached.':
        #     return True
        # else:
        #     return False
        vel_sum = abs(self.info.twist.twist.linear.x) + abs(self.info.twist.twist.linear.y) + abs(self.info.twist.twist.linear.z) + abs(self.info.twist.twist.angular.x) + abs(self.info.twist.twist.angular.y) + abs(self.info.twist.twist.angular.z)
        reach_flag = False
        if (self.info.pose.pose.position.x > -0.802) and (self.info.pose.pose.position.x < 0.398) and (self.info.pose.pose.position.y > -5.896) and (self.info.pose.pose.position.y < -4.696):
            reach_flag = True
        if (vel_sum < 0.03)  and reach_flag:
            return True
        else:
            return False 

    def get_topic(self):
        '''
        获取 Topic list，返回参数为 list
        '''
        return rospy.get_published_topics()


def main():
    n = ROSNavNode()

    print('send goal')
    n.send_goal()
    n.get_state()

    time.sleep(20)

if __name__  == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n')
        print('操作已取消')
        exit(0)
