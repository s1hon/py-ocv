import cv2
import numpy as np,sys
import os
import time

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
		for y in range(width):
			if gimg[x][y]<=blv1:
				if (gimg[x][y-1]>blv1 or y==0):
					os.system("echo G0 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
				elif y==(width-1):
					os.system("echo G1 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
			elif (gimg[x][y-1]<=blv1 and y>0):
				os.system("echo G1 X" + str(x/20) + " Y" + str((y-1)/20) + ">>" + fileid)
		print "direction1 -> %0.1f %%" %((x*100.0)/height)
def direction2():
	for y in range(0,width,10):
		for x in range(height):
			if gimg[x][y]<=blv2:
				if (gimg[x-1][y]>blv2 or x==0):
					os.system("echo G0 X" + str(x/20) + " Y" + str(y/20) + ">>" + fileid)
				elif y==(height-1):
					os.system("echo G1 X" + str(x/20) + " Y" + str(y/20) +">>" + fileid)
			elif (gimg[x-1][y]<=blv2 and x>0):
				os.system("echo G1 X" + str((x-1)/20) + " Y" + str(y/20) + ">>" + fileid)
		print "direction2 -> %0.1f %%" %((y*100.0)/width)

#def direction3():
#	for x in range(0,width,10):
#		for y in range(height):
#			if gimg[x][y]<=blv3:
#				if (gimg[y-1][x]>blv3 or y==0):
#					os.system("echo G0 X" + str(y/20) + " Y" + str(x/20) + ">>" + fileid)
#				elif y==(height-1):
#					os.system("echo G1 X" + str(y/20) + " Y" + str(x/20) +">>" + fileid)
#			elif (gimg[y-1][x]<=blv3 and y>0):
#				os.system("echo G1 X" + str((y-1)/20) + " Y" + str(x/20) + ">>" + fileid)
#		print "direction3 -> %0.1f %%" %((x*100.0)/height)
#pic to gray
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
height, width = gimg.shape

blv1=223
blv2=191
#blv3=159
child0=os.fork()
if child0!=0:
	child1=os.fork()

if child0==0:
	ppid0=os.getpid()
	print "Child0 PID:%d" %(ppid0)
	makefile(ppid0)
	direction1()
elif child1==0: 
	ppid1=os.getpid()
	print "Child1 PID:%d" %(ppid1)
	makefile(ppid1)
	direction2()

#elif child1==0: 
#	ppid2=os.getpid()
#	print "Child2 PID:%d" %(ppid2)
#	makefile(ppid2)
#	direction3()
else: 
	print "Parent PID:%d" %(os.getpid())


#cv2.imshow('pic-gray',gimg)
#cv2.waitKey(0)



#0-31	 black
#32-63   lv6
#64-95   lv5
#96-127  lv4
#128-159 lv3
#160-191 lv2
#192-223 lv1
#224-255 white
