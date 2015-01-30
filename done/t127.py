import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Queue

#make file save g-code
# def makefile(filename):
#   file_id = str(filename) + '.nc'
#   f = open(file_id,'w')
#   f.close()
#   return file_id


#direction top to bottom
def direction1(q,gimg):
    height, width = gimg.shape
    q_tmp="G17\nM3 S1000\nG0 X0 Y0\n"
    for x in range(0,height,10):
        print "%d" %(x)
        for y in range(width):
            if gimg[x][y]<=223: # black
                if (gimg[x][y-1]>223 or y==0): # white || y=0
                    q_tmp += "G0 X" + str(x/20) + " Y" + str(y/20) + "\n"
                elif y==(width-1): # if y has gone end.
                    q_tmp += "G1 X" + str(x/20) + " Y" + str(y/20) + "\n"
            elif (gimg[x][y-1]<=223 and y>0): # black && y > 0
                q_tmp += "G1 X" + str(x/20) + " Y" + str((y-1)/20) + "\n"
        print "direction1 -> %0.1f %%" %((x*100.0)/height)
    q.put(q_tmp)



def direction2(q,gimg):
    height, width = gimg.shape
    q_tmp=''
    for y in range(0,width,2):
        for x in range(height):
            if gimg[x][y]<=191:
                if gimg[x-1][y]<=191:
                    q_tmp += "G1 X" + str(x/20) + " Y" + str(y/20) + "\n"
                else:
                    q_tmp += "G0 X" + str(x/20) + " Y" + str(y/20) + "\n"
        q_tmp += "G0 X0" + " Y" + str(y/20) + "\n"
        print "direction2 -> %0.1f %%" %((y*100.0)/width)
    q.put(q_tmp)



#pic to gray
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

q1 = Queue()
q2 = Queue()

p0 = Process(target=direction1,args=(q1,gimg,))
p1 = Process(target=direction2,args=(q2,gimg,))
p0.start()
p1.start()
p0.join()
p1.join()

q1_r = q1.get()
q2_r = q2.get()

filename='t127'

file_id = str(filename) + '.nc'
f = open(file_id,'w')
f.write(q1_r+q2_r)
f.close()


#os.system(cat t127.nc  >>  t127-2.nc)


#if child0!=0:
#   child1=os.fork()

#if child0==0:
#   ppid0=os.getpid()
#   print "Child0 PID:%d" %(ppid0)
#   makefile(ppid0)
#   direction1()
#elif child1==0:
#   ppid1=os.getpid()
#   print "Child1 PID:%d" %(ppid1)
#       makefile(ppid1)
#        direction2()
#else:
#   print "Parent PID:%d" %(os.getpid())




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
