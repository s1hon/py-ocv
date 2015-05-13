import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AdaptiveTransferSpeed

def dirINIT(height,width,zoom,z_level_down,z_level_up,speed):
    q_tmp = "G17\rM3 S1000\r$H\r"
    q_tmp +="G0 X0 Y0\r"
    q_tmp += "G0 Z"+ z_level_down + "\r"
    q_tmp += "G1 F"+ speed +" X" + str(-height/zoom) +" Y0" + "\r"
    q_tmp += "G1 F"+ speed +" Y" + str(-width/zoom) + "\r"
    q_tmp += "G1 F"+ speed +" X0 " + "\r"
    q_tmp += "G1 F"+ speed +" Y0" + "\r"
    q_tmp += "G0 Z"+ z_level_up + "\r"
    return q_tmp


def direction0(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''

    for x in range(0,height,intr):
        if x%2==0:
            for y in range(width):
                if gimg[x][y]<=color: # black
                    if (gimg[x][y-1]>color or y==0): # white || y=0
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_down + "\r"                                         	#pen down
                    elif y==(width-1): # if y has gone end.
                        q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z"+ z_level_up + "\r"                                         	#pen up
                elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                    q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\r"         	#draw
                    q_tmp += "G0 Z"+ z_level_up + "\r"                                                 	#pen up
        else:
            for y in range((width-1),-1,-1):
                if gimg[x][y]<=color: # black
                    if (gimg[x][y-1]>color or y==0): # white || y=0
                        q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r" 		#draw
                        q_tmp += "G0 Z"+ z_level_up + "\r"                                     		#pen up
                    elif y==(width-1):
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_down + "\r"                                     		#pen down
                elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                    q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_down + "\r"                                             	#pen down
    q.send(q_tmp)
    q.close

def direction1(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''

    for y in range(0,width,intr):
        if y%2==0:
            for x in range(height):
                if gimg[x][y]<=color: # black
                    if (gimg[x-1][y]>color or x==0): # white || y=0
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_down + "\r"                                         	#pen down
                    elif x==(height-1): # if y has gone end.
                        q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z"+ z_level_up + "\r"                                         	#pen up
                elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                    q_tmp += "G1 F"+ speed +" X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\r"         	#draw
                    q_tmp += "G0 Z"+ z_level_up + "\r"                                                 	#pen up
        else:
            for x in range((height-1),-1,-1):
                if gimg[x][y]<=color: # black
                    if (gimg[x-1][y]>color or x==0): # white || y=0
                        q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z"+ z_level_up + "\r"                                         	#pen up
                    elif x==(height-1): # if y has gone end.
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_down + "\r"                                         	#pen down
                elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                    q_tmp += "G0 X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_down + "\r"                                                 	#pen down
    q.send(q_tmp)
    q.close

def direction2(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    the_range=[]

    for x in range(0,height-1,intr):
    	the_range.append([x,0])
    for y in range(0,width-1,intr):
    	the_range.append([0,y])
    for t_range in the_range:
        tx=t_range[0]
        ty=t_range[1]
        q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
        while (tx>=0 and tx<height and ty>=0 and ty<width):
            if gimg[tx][ty]<=color: # black
             	if (gimg[tx-intr][ty-intr]>color or tx==0 or ty==0):
                    q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_down + "\r"
                elif (tx==((height//3)*3) or ty==((width//3)*3)) :
                    q_tmp += "G1 F"+ speed +" X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_up + "\r"
            elif (gimg[tx-intr][ty-intr]<=color and tx>0 and ty>0):
                q_tmp += "G1 F"+ speed +" X" + str(-(tx-intr)/zoom) + " Y" + str(-(ty-intr)/zoom) + "\r"
                q_tmp += "G0 Z"+ z_level_up + "\r"
            tx+=intr
            ty+=intr

    q.send(q_tmp)
    q.close

def direction3(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    the_range=[]

    for x in range((height//3)*3,0,-intr):
    	the_range.append([x,0])
    for y in range(0,width,intr):
        the_range.append([(height//3)*3,y])
    for t_range in the_range:
        tx=t_range[0]
        ty=t_range[1]
        q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
        while (tx>=0 and ty>=0 and tx<height and ty<width):
       	    if gimg[tx][ty]<=color: # black
                if (tx+intr<=height and ty-intr>=0) :
                    if (gimg[tx+intr][ty-intr]>color):
                        q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_down + "\r"
                        if ty==(width//3)*3:
                            q_tmp += "G0 Z"+ z_level_up + "\r"
                    elif (tx==0 or ty==(width//3)*3 or tx==(height//3)*3 or ty==0):
                        q_tmp += "G1 F"+ speed +" X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z"+ z_level_up + "\r"
                elif (tx==(height//3)*3 or ty==0):
                    q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_down + "\r"
            elif (tx+intr<height and ty-intr>0):
                if (gimg[tx+intr][ty-intr]<=color and tx<height and ty>0):
                    q_tmp += "G1 F"+ speed +" X" + str(-(tx+intr)/zoom) + " Y" + str(-(ty-intr)/zoom) + "\r"
                    q_tmp += "G0 Z"+ z_level_up + "\r"

            tx-=intr
            ty+=intr
    q.send(q_tmp)
    q.close

def GetLevel(level):
    if level == 1 :
        return 223
    elif level == 2 :
        return 191
    elif level == 3 :
        return 159
    elif level == 4 :
        return 127
    elif level == 5 :
        return 95
    elif level == 6 :
        return 63
    elif level == 7 :
        return 31


def Gcode_Creater(print_id):
    ###### Setting ######
    
    zoom=3.0
    intr0=3
    intr1=1
    z_level_down= "5"
    z_level_up = "0"
    speed="5000"
    ###### Setting ######

    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
    g = cv2.imread('./static/upload_pic/'+print_id +'.jpg',cv2.IMREAD_GRAYSCALE)
    gimg = cv2.flip(g,0)	
    height, width = gimg.shape
 
    # parent_conn, child_conn = Pipe()
    q0x,q0 = Pipe()
    q1x,q1 = Pipe()
    q2x,q2 = Pipe()
    q3x,q3 = Pipe()
    
    p0 = Process(target=direction0,args=(q0,gimg,1,intr0,zoom,z_level_down,z_level_up,speed,))
    p1 = Process(target=direction1,args=(q1,gimg,2,intr0,zoom,z_level_down,z_level_up,speed,))
    p2 = Process(target=direction2,args=(q2,gimg,3,intr0,zoom,z_level_down,z_level_up,speed,))
    p3 = Process(target=direction3,args=(q3,gimg,5,intr0,zoom,z_level_down,z_level_up,speed,))

    init_r = dirINIT(height,width,zoom,z_level_down,z_level_up,speed,)
    p0.start()
    p1.start()
    p2.start()
    p3.start()

    pbar += 10

    q0_r = q0x.recv()
    q1_r = q1x.recv()
    q2_r = q2x.recv()
    q3_r = q3x.recv()

    p0.join()
    p1.join()
    p2.join()
    p3.join()

    f = open('./static/gcodes/'+str(print_id) + '.nc','w')
    f.write(init_r)
    f.write(q0_r)
    f.write(q1_r)
    f.write(q2_r)
    f.write(q3_r)
    f.write("G0 Z0\rG0 X0 Y0\r")
    f.close()

    pbar += 90
    time.sleep(0.5)
    pbar.finish()
