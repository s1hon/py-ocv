import cv2
import numpy as np,sys
import os
import time
import math
from multiprocessing import Process, Pipe

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
			q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"
			q_tmp += "G0 Z" + z_level_down + "\n"
		elif y==len(contours[x])-1:
			q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"
			q_tmp += "G1 F" + speed + " X"+ str(-contours[x][0][0][1]/zoom) + " Y" + str(-contours[x][0][0][0]/zoom) + "\n"
		else:
			q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"

	q_tmp += "G0 Z" + z_level_up + "\n"
	q.send(q_tmp)
	q.close()

def dirlevel(q,contours,zoom,z_level_down,z_level_up,speed):
        q_tmp=''
        list_area=[]
        tmp=[]

	for x in range(0,len(contours)):
		area = cv2.contourArea(contours[x])
		list_area.append(area)
	
	count=len(list_area)
	for x in range(0,count):
		if list_area[x] >=10:
			tmp.append( list_area.index(list_area[x]))


	for x in tmp:
#	for x in range(0,len(contours)):
        	for y in range(0,len(contours[x])):
                	if y==0:
                        	q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"
	                        q_tmp += "G0 Z" + z_level_down  + "\n"
        	        elif y==len(contours[x])-1:
                	        q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"
                        	q_tmp += "G1 F" + speed + " X"+ str(-contours[x][0][0][1]/zoom) + " Y" + str(-contours[x][0][0][0]/zoom) + "\n"
	                else:
        	                q_tmp += "G1 F" + speed + " X"+ str(-contours[x][y][0][1]/zoom) + " Y" + str(-contours[x][y][0][0]/zoom) + "\n"

        	q_tmp += "G0 Z" + z_level_up + "\n"
        q.send(q_tmp)
        q.close()

def dirGCODE(q,list_total,line,zoom,z_level_down,z_level_up,speed):
        q_tmp=''

        for line_x in range(0,line):
                if (len(list_total[line_x])%2 == 0):
                # len() = list size
#               print len(list_total[line_x])
                        for line_y in range (0, len(list_total[line_x])):
                                if (line_y%2==0):
                                        q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
                                        q_tmp += "G0 Z"+ z_level_down + "\n"
                                else:
                                        q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
                                        q_tmp += "G0 Z"+ z_level_up + "\n"

#               print list_total[line_x]
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
		if (x%2!=0):
			list_total[line].reverse()
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
	z_level_down="0.26"
	z_level_up="0"
	speed="5000"
	
#	img = cv2.imread('picture.jpg')
	g = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	pic = cv2.flip(g,0)
	height,width = pic.shape

	ret,thresh1 = cv2.threshold(pic,223,255,cv2.THRESH_BINARY_INV)
	ret,thresh2 = cv2.threshold(pic,159,255,cv2.THRESH_BINARY_INV)
	ret,thresh3 = cv2.threshold(pic,95,255,cv2.THRESH_BINARY_INV)
	
	image,contours1,hierarchy1=cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE,offset=(1,-1))
	image,contours2,hierarchy2=cv2.findContours(thresh2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE,offset=(1,-1))
	image,contours3,hierarchy3=cv2.findContours(thresh3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE,offset=(1,-1))
	
# outline pipe()
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
# color level pipe()
	q3x,q3 = Pipe()
	q4x,q4 = Pipe()
	q5x,q5 = Pipe()
	
	color_tmp=0
        white_tmp=0
        #count pixel color
        for x in range(0,height,1):
                for y in range(0,width,1):
                        if (pic[x][y]<=223):
                                color_tmp += pic[x][y]
                        else:
                                white_tmp+=1
        #count pixel average
        color_av = color_tmp//((height*width)-white_tmp)
        #decide color level
        if color_av >= 100:
                color_level = [1,3,5]
        else:
                color_level = [3,5,6]

	p0 = Process(target=diroutline,args=(q0,contours1,zoom,z_level_down,z_level_up,speed,))
	p1 = Process(target=dirlevel,args=(q1,contours2,zoom,z_level_down,z_level_up,speed,))
	p2 = Process(target=dirlevel,args=(q2,contours3,zoom,z_level_down,z_level_up,speed,))

	list_p3 = direction0(pic,color_level[0],intr0,)
        list_p4 = direction1(pic,color_level[1],intr0,)
        list_p5 = direction2(pic,color_level[2],intr0,)

	p3 = Process(target=dirGCODE,args=(q3,list_p3[0],list_p3[1],zoom,z_level_down,z_level_up,speed,))
        p4 = Process(target=dirGCODE,args=(q4,list_p4[0],list_p4[1],zoom,z_level_down,z_level_up,speed,))
        p5 = Process(target=dirGCODE,args=(q5,list_p5[0],list_p5[1],zoom,z_level_down,z_level_up,speed,))


	p0.start()
	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()

	q0_r = q0x.recv()
	q1_r = q1x.recv()
	q2_r = q2x.recv()
	q3_r = q3x.recv()
	q4_r = q4x.recv()
	q5_r = q5x.recv()

	p0.join()
	p1.join()
	p2.join()
	print("Outline-code done...")
	p3.join()
	p4.join()
	p5.join()
	print("Color level done...")	

	filename='outline'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(q0_r)
	f.write(q1_r)
	f.write(q2_r)
	f.write(q3_r)
	f.write(q4_r)
	f.write(q5_r)
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
