import cv2
import numpy as np,sys
import os
import time
import math
from multiprocessing import Process, Pipe


#--------------------
# Draw an outline-1 |
#--------------------
def filter0(list_total,line,zoom):
	list_tmp=[]
	list_clearup=[]
	
#---------------
# First filter |
#---------------
#------------------------------------
# Neighbor number save list_clearup |
#------------------------------------
	for x in range(0,line):
		list_tmp.append([])
		for y in range(1,len(list_total[x])):
#------------------------------^------------------------
# Because the next number before subtracting a number ,|
# so the range starting from 1			       |
#-------------------------------------------------------
			if (y != len(list_total[x])-1):
				if( (list_total[x][y][1] == list_total[x][y-1][1]+1) or (list_total[x][y][1] == list_total[x][y-1][1]+2)):
					list_tmp[x].append(list_total[x][y-1])
					list_tmp[x].append(list_total[x][y])
		if (len(list_tmp[x])!=0):
			for i in list_tmp[x]:
				if i not in list_clearup:
					list_clearup.append(i)
			list_tmp[x] = list_clearup
#------------------------------------------------------------------------
# Part list_clearup of list_total which has removed , and save list_tmp |
#------------------------------------------------------------------------
	list_t=[]
	line_t=0

	for x in range(0,line):
		list_t.append([])
		for y in list_total[x]:
			if y not in list_clearup:
				list_t[line_t].append(y)
		line_t += 1
		list_total[x] = list_t
	
#----------------
# Second filter |
#----------------
	list_tmp=[]
	list_clearup=[]

	for x in range(0,line_t):
		list_tmp.append([])
		for y in range(1,len(list_t[x])):
			if ( int (round (float (list_t[x][y][1])/zoom)) <= int( round (float (list_t[x][y-1][1])/zoom))+1):
				list_tmp[x].append(list_t[x][y-1])
				list_tmp[x].append(list_t[x][y])
		
		if (len(list_tmp[x])!=0):
			for i in list_tmp[x]:
				if i not in list_clearup:
					list_clearup.append(i)
			list_tmp[x] = list_clearup
	list_filter=[]	
	line_f=0

	for x in range(0,line_t):
		list_filter.append([])
		for y in list_t[x]:
			if y not in list_clearup:
				list_filter[line_f].append(y)
		line_f+=1
		list_t[x] = list_filter
	

#------------------------------------------
# Check whether the points correct or not |
#------------------------------------------
#	q_tmp=''
#	for x in range(0,line_f):
#		for y in range(0,len(list_filter[x])):
#			if (y%2==0):
#				q_tmp += "G0 X" + str(-list_filter[x][y][0]/zoom) + " Y" + str(-list_filter[x][y][1]/zoom) + "\n"
#				q_tmp += "G0 Z"+ z_level_down + "\n"
#			else:
#				q_tmp += "G1 F" + speed + " X" + str(-list_filter[x][y][0]/zoom) + " Y" + str(-list_filter[x][y][1]/zoom) + "\n"
#				q_tmp += "G0 Z"+ z_level_up + "\n"
#	q.send(q_tmp)
#	q.close()
	return list_filter,line_f

def outline(q,list_filter,line_f,zoom,z_level_down,z_level_up,speed):
#----------------------------------------------
# The point of each layer save to the len_tmp |
#----------------------------------------------
	len_tmp=[]
	for lx in range(0,line_f):
		len_tmp.append(len(list_filter[lx]))	
	
#-------------------------
# Draw an left and right |
#-------------------------
	q_tmp=''
	len_s=min(len_tmp)
	len_max=max(len_tmp)
	a=None
	while len_s <= len_max:
		y = len_s-1
		while y >= 0:
			for x in range(0,line_f):
				if (len(list_filter[x]) == len_s):
					if (a == None):
						a = list_filter[x][y][0]
						q_tmp += "G0 X" + str(-list_filter[x][y][0]/zoom) + " Y" + str(-list_filter[x][y][1]/zoom) + "\n"
					elif (a == list_filter[x][y][0]-3):
						a = list_filter[x][y][0]
						q_tmp += "G1 F" + speed + " X" + str(-list_filter[x][y][0]/zoom) + " Y" + str(-list_filter[x][y][1]/zoom) + "\n"
					else:
						a = list_filter[x][y][0]
						q_tmp += "G0 X" + str(-list_filter[x][y][0]/zoom) + " Y" + str(-list_filter[x][y][1]/zoom) + "\n"
			y-=1
		len_s+=2
		a=None

#----------------------------
# Draw an up top and bottom |
#----------------------------
	x_tmp=[]
	for x in range(0,line_f):
		for y in range(0,len(list_filter[x])):
			x_tmp.append(list_filter[x][y][0])
	
	list_tmp=[]
	count=0
	for x in range(0,line_f):
		list_tmp.append([])
		for y in range(0,len(list_filter[x])):
			if (list_filter[x][y][0] == min(x_tmp) or list_filter[x][y][0] == max(x_tmp)):
				list_tmp[count].append(list_filter[x][y])
		count+=1
		if (list_tmp[x] != []):
			for ty in range(0,len(list_tmp[x])):
				if (ty%2 == 0):
					q_tmp += "G0 X" + str(-list_tmp[x][ty][0]/zoom) + " Y" + str(-list_tmp[x][ty][1]/zoom) + "\n"
				else:
					q_tmp += "G1 F" + speed + " X" + str(-list_tmp[x][ty][0]/zoom) + " Y" + str(-list_tmp[x][ty][1]/zoom) + "\n"

	
	q.send(q_tmp)
	q.close()
		
#------------------------
# Draw an picture level |
#------------------------
def dirGCODE(q,list_total,line,zoom,z_level_down,z_level_up,speed):
	q_tmp=''
	for line_x in range(0,line):
#		-----------------
#		len() = list size
#		-----------------
#		print len(list_total[line_x])
		for line_y in range (0, len(list_total[line_x])):
			if (line_y%2==0):
				q_tmp += "G0 X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
				q_tmp += "G0 Z"+ z_level_down + "\n"
			else:
				q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
				q_tmp += "G0 Z"+ z_level_up + "\n"
	q.send(q_tmp)
	q.close()



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
#               if (x%2!=0):
#                       list_total[line].reverse()
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
#
#
#
	if (len(sys.argv) < 2):
		print "Enter picture's name"
	else :
		fn = str(sys.argv[0])
		pn = str(sys.argv[1])
	zoom=3
	intr0=3
	intr1=1
	z_level_down="4"
	z_level_up="0"
	speed="5000"
	g = cv2.imread(pn + '.jpg',cv2.IMREAD_GRAYSCALE)
	gimg=cv2.flip(g,0)
	height, width = gimg.shape

	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
#------------------------------
#	decide color level mode
#------------------------------
	color_tmp=0
	white_tmp=0
	#count pixel color
	for x in range(0,height,1):
		for y in range(0,width,1):
			if (gimg[x][y]<=223):
				color_tmp += gimg[x][y]
			else:
				white_tmp+=1
        #count pixel average
	color_av = color_tmp//((height*width)-white_tmp)
        #decide color level
	if color_av >= 100:
		color_level = [1,3,5]
	else:
		color_level = [3,5,6]

	list_p0 = direction0(gimg,color_level[0],intr0,)
#	filter_p0 = filter0(list_p0[0],list_p0[1],zoom,)
	p0 = Process(target=outline,args=(q0,list_p0[0],list_p0[1],zoom,z_level_down,z_level_up,speed,))
	p0.start()
	q0_r = q0x.recv()
	p0.join()
	filename = fn.split('.')[0]	
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(q0_r)
	f.close()
	print "Done!"






