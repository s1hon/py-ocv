import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AdaptiveTransferSpeed

#direction top to bottom
def direction0(q,gimg,level):
    color = GetLevel(level)
    height, width = gimg.shape
    intr=5
    zoom=20.0
    q_tmp="G17\rM3 S1000\rG0 X0 Y0\r"
    for x in range(0,height,intr):
        for y in range(width):
            if gimg[x][y]<=color: # black
                if (gimg[x][y-1]>color or y==0): # white || y=0
                    q_tmp += "G0 X" + str(x/zoom) + " Y" + str(y/zoom) + "\r"
                elif y==(width-1): # if y has gone end.
                    q_tmp += "G1 X" + str(x/zoom) + " Y" + str(y/zoom) + "\r"
            elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                q_tmp += "G1 X" + str(x/zoom) + " Y" + str((y-1)/zoom) + "\r"
    q.send(q_tmp)
    q.close

def direction1(q,gimg,level):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    intr=5
    zoom=20.0
    for y in range(0,width,intr):
        for x in range(height):
            if gimg[x][y]<=color: # black
                if (gimg[x-1][y]>color or x==0): # white || y=0
                    q_tmp += "G0 X" + str(x/zoom) + " Y" + str(y/zoom) + "\r"
                elif x==(height-1): # if y has gone end.
                    q_tmp += "G1 X" + str(x/zoom) + " Y" + str(y/zoom) + "\r"
            elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                q_tmp += "G1 X" + str((x-1)/zoom) + " Y" + str(y/zoom) + "\r"
    q.send(q_tmp)
    q.close


def direction2(q,gimg,level):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    intr=5
    zoom=20.0
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
                        q_tmp += "G1 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
                    elif ty==width: # if y has gone end.
                        q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
            elif (tx+intr<height and ty+intr<width) :
                if (gimg[tx+intr][ty+intr]<=color and ty>0): # black && y > 0
                    q_tmp += "G0 X" + str(tx/zoom) + " Y" + str((ty-1)/zoom) + "\r"
            tx+=intr
            ty+=intr

    q.send(q_tmp)
    q.close


def direction3(q,gimg,level):
    color = GetLevel(level)
    height, width = gimg.shape
    q_tmp=''
    intr=5
    zoom=20.0
    the_range=[]
    for x in range(0,height,intr):
        the_range.append([x,0])
        print "X %d " %(x)
    for y in range(0,width,intr):
        the_range.append([height-1,y])
    print(the_range)
    for t_range in the_range:
        print t_range
        tx=t_range[0]
        ty=t_range[1]
        q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
        print "X %d Y %d" %(tx,ty)
        while (tx-intr>=0 and ty+intr<=width):
            print "X1 %d Y1 %d" %(tx,ty)
            if gimg[tx][ty]<=color: # black
                    if (tx+intr<=height and ty-intr>=0) :
                        if (gimg[tx+intr][ty-intr]<=color):
                            q_tmp += "G1 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
                        else:
                            q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
            elif (tx+intr<=height and ty-intr>=0):
                if (gimg[tx+intr][ty-intr]<=color and tx>0 ):
                    q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\r"
            tx-=intr
            ty+=intr
    q.send(q_tmp)
    q.close
    print("d3 DONE!")


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
    # bar status
    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()

    #pic to gray
    gimg = cv2.imread('./static/upload_pic/'+print_id +'.jpg',cv2.IMREAD_GRAYSCALE)
    # parent_conn, child_conn = Pipe()
    q0x,q0 = Pipe()
    q1x,q1 = Pipe()
    q2x,q2 = Pipe()
    q3x,q3 = Pipe()
    p0 = Process(target=direction0,args=(q0,gimg,1,))
    p1 = Process(target=direction1,args=(q1,gimg,2,))
    p2 = Process(target=direction2,args=(q2,gimg,3,))
    p3 = Process(target=direction3,args=(q3,gimg,5,))
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
    pbar += 20

    p1.join()
    pbar += 20

    p2.join()
    pbar += 20

    p3.join()
    pbar += 20


    f = open('./static/gcodes/'+str(print_id) + '.nc','w')
    f.write(q0_r)
    f.write(q1_r)
    f.write(q2_r)
    f.write(q3_r)
    f.close()
    pbar += 10
    time.sleep(0.5)
    pbar.finish()

#cv2.imshow('pic-gray',gimg)
#cv2.waitKey(0)
#0-31 black
#32-63
#64-95
#96-127
#128-159
#160-191
#192-223
#224-255 white