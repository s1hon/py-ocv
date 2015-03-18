import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AdaptiveTransferSpeed

def dirINIT(height,width,zoom):
    q_tmp="G17\rM3 S1000\rG0 X0 Y0\r"
    q_tmp += "G0 Z2" + "\r"
    q_tmp += "G1 X" + str(-(height-1)/zoom) +" Y0" + "\r"
    q_tmp += "G1 Y" + str(-(width-1)/zoom) + "\r"
    q_tmp += "G1 X0 " + "\r"
    q_tmp += "G1 Y0" + "\r"
    q_tmp += "G0 Z0" + "\r"
    return q_tmp


def direction0(q,gimg,level,intr,zoom):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''

    for x in range(0,height,intr):
        if x%2==0:
            for y in range(width):
                if gimg[x][y]<=color: # black
                    if (gimg[x][y-3]>color or y==0): # white || y=0
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"                                         	#pen down
                    elif y==(width-1): # if y has gone end.
                        q_tmp += "G1 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z0" + "\r"                                         	#pen up
                elif (gimg[x][y-3]<=color and y>0): # black && y > 0
                    q_tmp += "G1 X" + str(-x/zoom) + " Y" + str(-(y-3)/zoom) + "\r"         	#draw
                    q_tmp += "G0 Z0" + "\r"                                                 	#pen up
        else:
            for y in range((width-1),-1,-3):
                if gimg[x][y]<=color: # black
                    if (gimg[x][y-3]>color or y==0): # white || y=0
                        q_tmp += "G1 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r" 		#draw
                        q_tmp += "G0 Z0" + "\r"                                     		#pen up
                    elif y==(width-1):
                        q_tmp += "G0 F800 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"                                     		#pen down
                elif (gimg[x][y-3]<=color and y>0): # black && y > 0
                    q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-3)/zoom) + "\r"
                    q_tmp += "G0 Z2" + "\r"                                             	#pen down
    q.send(q_tmp)
    q.close

def direction1(q,gimg,level,intr,zoom):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''

    for y in range(0,width,intr):
        if y%2==0:
            for x in range(height):
                if gimg[x][y]<=color: # black
                    if (gimg[x-3][y]>color or x==0): # white || y=0
                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"                                         	#pen down
                    elif x==(height-1): # if y has gone end.
                        q_tmp += "G1 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z0" + "\r"                                         	#pen up
                elif (gimg[x-3][y]<=color and x>0): # black && y > 0
                    q_tmp += "G1 X" + str(-(x-3)/zoom) + " Y" + str(-y/zoom) + "\r"         	#draw
                    q_tmp += "G0 Z0" + "\r"                                                 	#pen up
        else:
            for x in range((height-1),-1,-3):
                if gimg[x][y]<=color: # black
                    if (gimg[x-3][y]>color or x==0): # white || y=0
                        q_tmp += "G1 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"     	#draw
                        q_tmp += "G0 Z0" + "\r"                                         	#pen up
                    elif x==(height-1): # if y has gone end.
                        q_tmp += "G0 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"                                         	#pen down
                elif (gimg[x-3][y]<=color and x>0): # black && y > 0
                    q_tmp += "G0 X" + str(-(x-3)/zoom) + " Y" + str(-y/zoom) + "\r"
                    q_tmp += "G0 Z2" + "\r"                                                 	#pen down
    q.send(q_tmp)
    q.close

def direction2(q,gimg,level,intr,zoom):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    the_range=[]

    for x in range(height-1,0,-intr):
        the_range.append([x,0])
    for y in range(0,width,intr):
        the_range.append([0,y])
    for t_range in the_range:
        tx=t_range[0]
        ty=t_range[1]
        q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
        while (tx>=0 and tx+intr<height and ty>=0 and ty+intr<width ):
            if gimg[tx][ty]<=color: # black
                if (tx+intr<=height and ty+intr<=width) :
                    if (gimg[tx+intr][ty+intr]<=color or ty==0): # white || y=0
                        q_tmp += "G1 F800 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"
                    elif ty==width: # if y has gone end.
                        q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z0" + "\r"
            elif (tx+intr<height and ty+intr<width) :
                if (gimg[tx+intr][ty+intr]<=color and ty>0): # black && y > 0
                    q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-(ty-1)/zoom) + "\r"
                    q_tmp += "G0 Z0" + "\r"
            tx+=intr
            ty+=intr

    q.send(q_tmp)
    q.close


def direction3(q,gimg,level,intr,zoom):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    the_range=[]

    for x in range(0,height,intr):
        the_range.append([x,0])
    for y in range(0,width,intr):
        the_range.append([height-1,y])
    for t_range in the_range:
        tx=t_range[0]
        ty=t_range[1]
        q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
        while (tx-intr>=0 and ty+intr<=width):
            if gimg[tx][ty]<=color: # black
                if (tx+intr<=height and ty-intr>=0) :
                    if (gimg[tx+intr][ty-intr]<=color):
                        q_tmp += "G1 F800 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z2" + "\r"
                    else:
                        q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                        q_tmp += "G0 Z0" + "\r"
            elif (tx+intr<=height and ty-intr>=0):
                if (gimg[tx+intr][ty-intr]<=color and tx>0 ):
                    q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\r"
                    q_tmp += "G0 Z0" + "\r"
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
    
    zoom=80.0
    intr0=5
    intr1=3

    ###### Setting ######

    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
    gimg = cv2.imread('./static/upload_pic/'+print_id +'.jpg',cv2.IMREAD_GRAYSCALE)
    height, width = gimg.shape
 
    # parent_conn, child_conn = Pipe()
    q0x,q0 = Pipe()
    q1x,q1 = Pipe()
    q2x,q2 = Pipe()
    q3x,q3 = Pipe()
    
    p0 = Process(target=direction0,args=(q0,gimg,1,intr0,zoom,))
    p1 = Process(target=direction1,args=(q1,gimg,2,intr0,zoom,))
    p2 = Process(target=direction0,args=(q2,gimg,3,intr1,zoom,))
    p3 = Process(target=direction1,args=(q3,gimg,5,intr1,zoom,))

    init_r = dirINIT(height,width,zoom)
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
    f.close()

    pbar += 90
    time.sleep(0.5)
    pbar.finish()
