#!/usr/bin/env python
#coding=utf-8
import rospy
#倒入自定义的数据类型
import time
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import numpy as np
import threading

# GLOBAL VARIABLES
lane_vel = Twist()
angularScale = 6       # 180/30
servodata=0
traffic_light_data=0

def thread_job():

    rospy.spin()

def lanecallback(msg):
    global lane_vel
    lane_vel = msg
    _servoCmdMsg = msg.angular.z * angularScale + 90 
    global servodata
    servodata = min(max(0, _servoCmdMsg), 180)
    servodata=100-servodata*100/180
    #rospy.loginfo('lane_vel.angular.z = %f',lane_vel.angular.z)

def lightcallback(data):
    global traffic_light_data
    traffic_light_data=data.data
    #rospy.loginfo(rospy.get_caller_id() + "traffic_light_data is %s", traffic_light_data)



def kineticCtrl():

    #Publisher 函数第一个参数是话题名称，第二个参数 数据类型，现在就是我们定义的msg 最后一个是缓冲区的大小
    #queue_size: None（不建议）  #这将设置为阻塞式同步收发模式！
    #queue_size: 0（不建议）#这将设置为无限缓冲区模式，很危险！
    #queue_size: 10 or more  #一般情况下，设为10 。queue_size太大了会导致数据延迟不同步。

    pub1 = rospy.Publisher('/bluetooth/received/manul', Int32 , queue_size=10)
    pub2 = rospy.Publisher('/auto_driver/send/direction', Int32 , queue_size=10)
    pub3 = rospy.Publisher('/auto_driver/send/speed', Int32 , queue_size=10)
    pub4 = rospy.Publisher('/auto_driver/send/gear', Int32 , queue_size=10)
    
    manul=0       # 0 - Automatic
    speed=7.5     #SPEED
    direction=50  # 0-LEFT-50-RIGHT-100
    gear=1        # 1 - Drive, 2 - Stop 

    cmd_vel = Twist()
    flag=0
    p_flag=1
    servodata_list=[]
    n_loop=1

    rospy.init_node('kineticCtrl', anonymous=True)

    add_thread = threading.Thread(target = thread_job)

    add_thread.start()

    rate = rospy.Rate(4) # 1hz,0.125/8 sec
    rospy.Subscriber("/lane_vel", Twist, lanecallback)
    rospy.Subscriber("/traffic_light", Int32, lightcallback)
    
    #更新频率是5hz(geng-gai)
    rospy.loginfo(rospy.is_shutdown())
    n=5
    servodata_list = n * [servodata]						
    while not rospy.is_shutdown(): 
        # KINETIC CONTROL CODE HERE
        #sona_data=rospy.wait_for_message("/vcu/SupersonicDistance", Int32, timeout=0.2)
        #traffic_light=rospy.wait_for_message("/traffic_light", Int32,timeout=None)
        #traffic_signs=rospy.wait_for_message("/traffic_signs", Int32,timeout=None)
   
        # if State is GO AROUND
        #if(lane_vel.linear.x == 0): # STOP SIGNAL FROM HILENS
     
 	
        servodata_list[0:n-1] = servodata_list[1:n]
        servodata_list[n-1] = servodata
        #servodata_mean = np.mean(servodata_list)*n
        sumii = 0

        for i in servodata_list:
            sumii += i
            #print("servodata %f",i)
        servodata_mean = sumii/n
        #print("servodata %f %f",servodata_mean,servodata)
        
        #servodata_mean=servodata

        # WRITE YOUR CONDITION STATEMENT HERE
        # USE (traffic_light_data)
        # TO CHANGE: GEAR, DIRECTION(IF DRIVE, USE servodata_mean)
        #   
        if (traffic_light_data == 0):#red light from hilens
            gear = 2

        elif (traffic_light_data == 1): # green light from hilens
            gear = 1
            direction = servodata_mean     
             
             
        
        pub1.publish(manul)
        pub2.publish(direction)
        pub3.publish(speed)
        pub4.publish(gear)   
        rate.sleep()

if __name__ == '__main__':
    kineticCtrl()
