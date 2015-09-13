import cv2
import numpy as np,sys
import os
import time
import math
from multiprocessing import Process, Pipe

#Frame
def dirINIT(height,width,zoom,z_level_down,z_level_up,speed):
	q_tmp = "G17\nM3 S1000\n$H\n"
    	q_tmp += "G0 Z0\n"
    	q_tmp += "G0 X0 Y0\n"
    	q_tmp += "G0 Z"+ z_level_down + "\n"
    	q_tmp += "G1 F"+ speed +" X" + str(-height/zoom) +" Y0" + "\n"
    	q_tmp += "G1 F"+ speed +" Y" + str(-width/zoom) + "\n"
    	q_tmp += "G1 F"+ speed +" X0 " + "\n"
    	q_tmp += "G1 F"+ speed +" Y0" + "\n"
    	q_tmp += "G0 Z"+ z_level_up + "\n"
    	return q_tmp

#produce G-code
def diroutline(q,contours,zoom,z_level_down,z_level_up,speed):
	q_tmp=''
	list_area=[]
	tmp=[]
	for x in range(0,len(contours)):
		area = cv2.contourArea(contours[x])
		list_area.append(area)
	
		
	x=list_area.index(max(list_area))
	for y in range(0,len(contours[x])):
		if y==0:
			q_tmp += "G0 X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"
		else:
			q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"

	q.send(q_tmp)
	q.close()

#direction top to bottom
def direction0(gimg,level,intr):
	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''
	line=0
	list_total=[]
	
	for x in range(0,height,intr):
		list_total.append([])
		for y in range(0,width):
			if (gimg[x][y]<=color):
				if (gimg[x][y-1]>color or y==0):
					list_total[line].append([x,y])
				elif (y==(width//zoom)*3):
					list_total[line].append([x,y])
			elif (gimg[x][y-1]<=color and y>0):
				list_total[line].append([x,y])
#		if (x%2!=0):
#			list_total[line].reverse()
		line+=1

	return list_total,line

def direction1(gimg,level,intr):
	color = GetLevel(level)
        height, width = gimg.shape
        q_tmp=''
        line=0
        list_total=[]

        for y in range(0,width,intr):
                list_total.append([])
                for x in range(0,height):
                        if (gimg[x][y]<=color):
                                if (gimg[x-1][y]>color or x==0):
                                        list_total[line].append([x,y])
                                elif (x==(height//zoom)*3):
                                        list_total[line].append([x,y])
                        elif (gimg[x-1][y]<=color and x>0):
                                list_total[line].append([x,y])
                if (y%2!=0):
                        list_total[line].reverse()
                line+=1
	return list_total,line

def direction2(gimg,level,intr):
	color = GetLevel(level)
        height, width = gimg.shape
        q_tmp=''
        line=0
        list_total=[]	
	
	for x in range((height//intr)*intr,0,-intr):
		list_total.append([])
		y=0
		while (x>=0 and y<width and x<height and y>=0):
			if (gimg[x][y]<=color):
				if (gimg[x-intr][y-intr]>color or x==0 or y==0):
					list_total[line].append([x,y])
#					q_tmp += "G0 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
				elif (x==(height//intr)*intr or y==(width//intr)*intr):
					list_total[line].append([x,y])
#					q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n"	
			elif (gimg[x-intr][y-intr]<=color and x>0 and y>0):
				list_total[line].append([x,y])
#				q_tmp += "G1 X" + str(-(x-intr)/3) + " Y" + str(-(y-intr)/3) + "\n"
			y+=intr
			x+=intr
		if (line%2!=0):
                	list_total[line].reverse()
		line+=1
	
	for y in range(0,(width//intr)*intr,intr):
		list_total.append([])
		x=0
		while (x>=0 and y<width and x<height and y>=0):
			if (gimg[x][y]<=color):
                                if (gimg[x-intr][y-intr]>color or x==0 or y==0):
					 list_total[line].append([x,y])
#                                        q_tmp += "G0 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                                elif (x==(height//intr)*intr or y==(width//intr)*intr):
					 list_total[line].append([x,y])
#                                        q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                        elif (gimg[x-intr][y-intr]<=color and x>0 and y>0):
				 list_total[line].append([x,y])
#                                q_tmp += "G1 X" + str(-(x-intr)/3) + " Y" + str(-(y-intr)/3) + "\n"
			x+=intr
			y+=intr
		if (line%2!=0):
			list_total[line].reverse()
		line+=1
	return list_total,line
	
def direction3(gimg,level,intr):
	color = GetLevel(level)
        height, width = gimg.shape
        q_tmp=''
        line=0
        list_total=[]

	for x in range((height//intr)*intr,0,-intr):
		list_total.append([])
		y=(width//intr)*intr
                while (x>=0 and y<width and x<height and y>=0):
			#test			
#                        q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
			if (gimg[x][y]<=color):
				if (x-intr>=0 and y+intr<width):
	                                if (gimg[x-intr][y+intr]>color or x==0 or y==(width//intr)*intr):
        	                                 list_total[line].append([x,y])
#               	                         q_tmp += "G0 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                        	        elif (x==(height//intr)*intr or y==0):
                                	         list_total[line].append([x,y])
#                                       	 q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                        elif (x-intr>=0 and y+intr<=width):
				if (gimg[x-intr][y+intr]<=color and x>0 and y>0):
                                 	list_total[line].append([x,y])
#                                	q_tmp += "G1 X" + str(-(x-intr)/3) + " Y" + str(-(y-intr)/3) + "\n"

                        x+=intr
                        y-=intr
		if (line%2!=0):
                        list_total[line].reverse()
                line+=1

	for y in range((width//intr)*intr,0,-intr):
		list_total.append([])
		x=0
		while (x>=0 and y<width and x<height and y>=0):
#			q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n" 
			if (gimg[x][y]<=color):
				if (x-intr>=0 and y+intr<=width):
	                                if (gimg[x-intr][y+intr]>color or x==0 or y==(width//intr)*intr):
        	                                 list_total[line].append([x,y])
#               	                         q_tmp += "G0 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                        	        elif (x==(height//intr)*intr or y==0):
                                	         list_total[line].append([x,y])
#                                       	 q_tmp += "G1 X" + str(-x/3) + " Y" + str(-y/3) + "\n"
                        elif (x-intr>=0 and y+intr<=width):
				if  (gimg[x-intr][y+intr]<=color and x>0 and y>0):
                                 	list_total[line].append([x,y])
#                                	q_tmp += "G1 X" + str(-(x-intr)/3) + " Y" + str(-(y-intr)/3) + "\n"
			x+=intr
			y-=intr
		if (line%2!=0):
                        list_total[line].reverse()
                line+=1
        return list_total,line

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
#set up
	zoom=3
	intr0=3
	intr1=1
	z_level_down="4"
	z_level_up="0"
	speed="5000"
	
	img = cv2.imread('picture.jpg')
	g = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	pic = cv2.flip(g,0)	

	ret,thresh2 = cv2.threshold(pic,223,255,cv2.THRESH_BINARY_INV)
	image,contours,hierarchy=cv2.findContours(thresh2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE,offset=(1,-1))
	
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
	


	p0 = Process(target=diroutline,args=(q0,contours,zoom,z_level_down,z_level_up,speed,))

	p0.start()

	q0_r = q0x.recv()

	p0.join()

	print("Enter the G-code.....")
	filename='outline'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(q0_r)
	f.close()

#cv2.imshow('pic-gray',pic)
#cv2.waitKey(0)
#0-31 black
#32-63
#64-95
#96-127
#128-159
#160-191
#192-223
#224-255 white
