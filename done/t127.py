import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe


#direction top to bottom
def direction0(q,gimg,level):
	color = GetLevel(level)

	height, width = gimg.shape
	zoom=40.0
	intr=5
	q_tmp="G17\nM3 S1000\n$H\n"
	print "%d %d" %(height,width)
	
	q_tmp += "G0 X0 Y0" + "\n"
	q_tmp += "G0 Z2" + "\n"
	q_tmp += "G1 F800 X" + str(-(height-1)/zoom) +" Y0" + "\n"
	q_tmp += "G1 F800 Y" + str(-(width-1)/zoom) + "\n"
	q_tmp += "G1 F800 X0 " + "\n"
	q_tmp += "G1 F800 Y0" + "\n"
	q_tmp += "G0 Z0" + "\n"

	for x in range(0,height,intr):
		if x%2==0:
			for y in range(width):
				if gimg[x][y]<=color: # black
                               		if (gimg[x][y-1]>color or y==0): # white || y=0
                                       		q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                                       		q_tmp += "G0 Z3" + "\n"						#pen down
                               		elif y==(width-1): # if y has gone end.
                                       		q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                       		q_tmp += "G0 Z0" + "\n"						#pen up
                       		elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                               		q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"		#draw
                               		q_tmp += "G0 Z0" + "\n"							#pen up
		else:	
			for y in range((width-1),-1,-1):
                                if gimg[x][y]<=color: # black
                                        if (gimg[x][y-1]>color or y==0): # white || y=0
                                                q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                                q_tmp += "G0 Z0" + "\n"						#pen up
                                        elif y==(width-1):
                                                q_tmp += "G0 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                                                q_tmp += "G0 Z3" + "\n"						#pen down
                                elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"
                                        q_tmp += "G0 Z3" + "\n"							#pen down

	q.send(q_tmp)
	q.close
	print("d0 DONE!")

def direction1(q,gimg,level):
	color = GetLevel(level)
	height, width = gimg.shape
	q_tmp=''
	intr=5
	zoom=40.0
	for y in range(0,width,intr):
		if y%2==0:
			for x in range(height):
				if gimg[x][y]<=color: # black
					if (gimg[x-3][y]>color or x==0): # white || y=0
						q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
						q_tmp += "G0 Z3" + "\n"						#pen down
					elif x==(height-1): # if y has gone end.
						q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
						q_tmp += "G0 Z0" + "\n"						#pen up
				elif (gimg[x-1][y]<=color and x>0): # black && y > 0
					q_tmp += "G1 F800 X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\n"		#draw
					q_tmp += "G0 Z0" + "\n"							#pen up
		else:
			for x in range((height-1),-1,-1):
				if gimg[x][y]<=color: # black
                                        if (gimg[x-1][y]>color or x==0): # white || y=0
                                                q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                                q_tmp += "G0 Z0" + "\n"						#pen up
                                        elif x==(height-1): # if y has gone end.
                                                q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                                                q_tmp += "G0 Z3" + "\n"						#pen down
                                elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                                        q_tmp += "G0 X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\n"
                                        q_tmp += "G0 Z3" + "\n"							#pen down
	q.send(q_tmp)
	q.close
	print("d1 DONE!")

def direction2(q,gimg,level):
	color = GetLevel(level)
	height, width = gimg.shape
	q_tmp=''
	intr=5
	zoom=40.0
	the_range=[]

	for x in range(height-1,0,-intr):
		the_range.append([x,0])
	for y in range(0,width,intr):
		the_range.append([0,y])
#	print(the_range)
	for t_range in the_range:
#		print t_range
		tx=t_range[0]
		ty=t_range[1]
		q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
#		print "X %d Y %d" %(tx,ty)
		while (tx>=0 and tx+intr<height and ty>=0 and ty+intr<width ):
#			print "X1 %d Y1 %d" %(tx,ty)
			if gimg[tx][ty]<=color: # black
				if (tx+intr<=height and ty+intr<=width) :
					if (gimg[tx+intr][ty+intr]<=color or ty==0): # white || y=0
						q_tmp += "G1 F800 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
						q_tmp += "G0 Z2" + "\n"
					elif ty==width: # if y has gone end.
						q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
						q_tmp += "G0 Z0" + "\n"
			elif (tx+intr<height and ty+intr<width) :
				if (gimg[tx+intr][ty+intr]<=color and ty>0): # black && y > 0
					q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-(ty-1)/zoom) + "\n"
					q_tmp += "G0 Z0" + "\n"
			tx+=intr
			ty+=intr

	q.send(q_tmp)
	q.close
	print("d2 DONE!")

def direction3(q,gimg,level):
	color = GetLevel(level)
	height, width = gimg.shape
	q_tmp=''
	intr=5
	zoom=40.0
	the_range=[]
	for x in range(0,height,intr):
                the_range.append([x,0])
#		print "X %d " %(x)
        for y in range(0,width,intr):
                the_range.append([height-1,y])
#		print(the_range)
        for t_range in the_range:
#		print t_range
                tx=t_range[0]
                ty=t_range[1]
                q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
#		print "X %d Y %d" %(tx,ty)
                while (tx-intr>=0 and ty+intr<=width):
#			print "X1 %d Y1 %d" %(tx,ty)
                        if gimg[tx][ty]<=color: # black
                                if (tx+intr<=height and ty-intr>=0) :
					if (gimg[tx+intr][ty-intr]<=color):
						q_tmp += "G1 F800 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
						q_tmp += "G0 Z2" + "\n"
					else:
						q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
						q_tmp += "G0 Z0" + "\n"
			elif (tx+intr<=height and ty-intr>=0):
				if (gimg[tx+intr][ty-intr]<=color and tx>0 ):
					q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
					q_tmp += "G0 Z0" + "\n"
                        tx-=intr
                        ty+=intr
	

	q.send(q_tmp)
	q.close
	print("d3 DONE!")

def direction4(q,gimg,level):
	color = GetLevel(level)
	height, width = gimg.shape
	q_tmp=''
	intr=3
	zoom=40.0
	for x in range(0,height,intr):
		if x%2==0:
			for y in range(0,width,3):
				if gimg[x][y]<=color: # black
                               		if (gimg[x][y-3]>color or y==0): # white || y=0
                                       		q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                                       		q_tmp += "G0 Z2" + "\n"						#pen down
                               		elif y==(width-1): # if y has gone end.
                                       		q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                       		q_tmp += "G0 Z0" + "\n"						#pen up
                       		elif (gimg[x][y-3]<=color and y>0): # black && y > 0
                               		q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-(y-3)/zoom) + "\n"		#draw
                               		q_tmp += "G0 Z0" + "\n"							#pen up
		else:	
			for y in range((width-1),-1,-3):
                                if gimg[x][y]<=color: # black
                                        if (gimg[x][y-3]>color or y==0): # white || y=0
                                                q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                                q_tmp += "G0 Z0" + "\n"						#pen up
                                        elif y==(width-1):
                                                q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"
                                                q_tmp += "G0 Z2" + "\n"						#pen down
                                elif (gimg[x][y-3]<=color and y>0): # black && y > 0
                                        q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-3)/zoom) + "\n"
                                        q_tmp += "G0 Z2" + "\n"							#pen down

	q.send(q_tmp)
	q.close
	print("d2 DONE!")

def direction5(q,gimg,level):
	color = GetLevel(level)
	height, width = gimg.shape
	q_tmp=''
	intr=3
	zoom=40.0
	for y in range(0,width,intr):
		if y%2==0:
			for x in range(0,height,3):
				if gimg[x][y]<=color: # black
					if (gimg[x-3][y]>color or x==0): # white || y=0
						q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
						q_tmp += "G0 Z2" + "\n"						#pen down
					elif x==(height-1): # if y has gone end.
						q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
						q_tmp += "G0 Z0" + "\n"						#pen up
				elif (gimg[x-3][y]<=color and x>0): # black && y > 0
					q_tmp += "G1 F800 X" + str(-(x-3)/zoom) + " Y" + str(-y/zoom) + "\n"		#draw
					q_tmp += "G0 Z0" + "\n"							#pen up
		else:
			for x in range((height-1),-1,-3):
				if gimg[x][y]<=color: # black
                                        if (gimg[x-3][y]>color or x==0): # white || y=0
                                                q_tmp += "G1 F800 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"	#draw
                                                q_tmp += "G0 Z0" + "\n"						#pen up
                                        elif x==(height-1): # if y has gone end.
                                                q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                                                q_tmp += "G0 Z2" + "\n"						#pen down
                                elif (gimg[x-3][y]<=color and x>0): # black && y > 0
                                        q_tmp += "G0 X" + str(-(x-3)/zoom) + " Y" + str(-y/zoom) + "\n"
                                        q_tmp += "G0 Z2" + "\n"							#pen down
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


if __name__ == '__main__':
	#pic to gray
	gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
#	gimg=cv2.flip(g,0)
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
#	p0 = Process(target=direction0,args=(q0,gimg,1,))
	p1 = Process(target=direction1,args=(q1,gimg,3,))
#	p2 = Process(target=direction4,args=(q2,gimg,5,))
#	p3 = Process(target=direction5,args=(q3,gimg,6,))
#	p0.start()
	p1.start()
#	p2.start()
#	p3.start()

#	q0_r = q0x.recv()
	q1_r = q1x.recv()
#	q2_r = q2x.recv()
#	q3_r = q3x.recv()
	print("End of Get the Pipe....")

#	p0.join()
	print("p0 end!")

	p1.join()
	print("p1 end!")

#	p2.join()
	print("p2 end!")

#	p3.join()
	print("p3 end!")

	print("Make the file.....")
	filename='t127'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
#	f.write(q0_r)
	f.write(q1_r)
#	f.write(q2_r)
#	f.write(q3_r)
	f.close()

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
