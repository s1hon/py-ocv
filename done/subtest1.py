import cv2
import numpy as np,sys
import os
import time
import subprocess

#make file save g-code
def makefile(filename):
	global fileid
	fileid = str(filename) + '.nc'
	f = open(fileid,'w')
	f.close()
#direction top to bottom
def direction1():
	os.system("echo G17" + ">>" + fileid)
	os.system("echo M3 S1000" + ">>" + fileid)
	os.system("echo G0 X0 Y0" + ">>" + fileid)
	for x in range(0,height,10):
		print "%d" %(x)
		for y in range(width):
			if gimg[x][y]<=223: # black
				if (gimg[x][y-1]>223 or y==0): # white || y=0
					os.system("echo G0 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
				elif y==(width-1): # if y has gone end.
					os.system("echo G1 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
			elif (gimg[x][y-1]<=223 and y>0): # black && y > 0
				os.system("echo G1 X" + str(x/20) + " Y" + str((y-1)/20) + ">>" + fileid)

		print "direction1 -> %0.1f %%" %((x*100.0)/height)
def direction2():
	cx=0
	os.system("echo G17" + ">>" + fileid)
	os.system("echo M3 S1000" + ">>" + fileid)
	os.system("echo G0 X0 Y0" + ">>" + fileid)
	for y in range(0,width,2):
		for x in range(height):
			if gimg[x][y]<=191:
				if gimg[x-1][y]<=191:
					os.system("echo G1 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
				else:
					os.system("echo G0 X" + str(x/20) + " Y" + str(y/20) +">>" + fileid)
		os.system("echo G0 X" + str(cx) + " Y" + str(y/20) + ">>" + fileid)
		print "direction2 -> %0.1f %%" %((y*100.0)/width)
#pic to gray
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
height, width = gimg.shape

child0=subprocess.call()
if child0!=0:
	child1=subprocess.Popen()

if child0==0:
	ppid0=()
	print "Child0 PID:%d" %(ppid0)
	makefile(ppid0)
	direction1()
elif child1==0:
	ppid1=os.getpid()
	print "Child1 PID:%d" %(ppid1)
        makefile(ppid1)
        direction2()
else:
	print "Parent PID:%d" %(os.getpid())




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
