import cv2
import numpy as np,sys
import os
import time
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
def dirGCODE(q,list_total,line,zoom,z_level_down,z_level_up,speed):
	q_tmp=''
	list_tmp=[]
	list_clearup=[]
	list_new=[]
 	line_new=0
#	2 list compare	repertes del
#	a=[1,1,2,3,4]
#	b=[1]
#	c=set(a)-set(b)
#	print list(c)
	
#	filter repeated list
#	c=[[1,2],[1,2],[2,3],[4,5]]
#	b=[[1,2]]
#	d=[]
#	for a in c:
#		if a not in b:
#			d.append(a)
#	c = d
#	print d
	for line_x in range(0,line):
               	# len() = list size
#		print len(list_total[line_x])		
#		print list_total[line_x]
		list_tmp.append([])
		for line_y in range(0,len(list_total[line_x])):
#			print list_total[line_x][line_y]			
			if(list_total[line_x][line_y][1]==list_total[line_x][line_y-1][1]+1):
#				print list_total[line_x][line_y-1]
#				print list_total[line_x][line_y]
				list_tmp[line_x].append(list_total[line_x][line_y-1])
				list_tmp[line_x].append(list_total[line_x][line_y])
		if (len(list_tmp[line_x])!=0):
			for i in list_tmp[line_x]:
				if i not in list_clearup:
					list_clearup.append(i)
			list_tmp[line_x] = list_clearup
#	print list_tmp
#	print list_clearup
	
	for line_x in range(0,line):
		list_new.append([])
		for total_tmp in list_total[line_x]:
			if total_tmp not in list_clearup:
				list_new[line_new].append(total_tmp)
		line_new+=1
		list_total[line_x]=list_new
#	print list_new

#	test

#	for new_x in range(0,line_new):
#		print list_new[new_x]
	
	for new_x in range(0,line_new):
		for new_y in range(0,len(list_new[new_x])):
			if (new_y%2==0):
                                q_tmp += "G0 X" + str(-list_new[new_x][new_y][0]/zoom) + " Y" + str(-list_new[new_x][new_y][1]/zoom) + "\n"
                                q_tmp += "G0 Z"+ z_level_down + "\n"
                        else:
                                q_tmp += "G1 F" + speed + " X" + str(-list_new[new_x][new_y][0]/zoom) + " Y" + str(-list_new[new_x][new_y][1]/zoom) + "\n"
                                q_tmp += "G0 Z"+ z_level_up + "\n"


#	for new_x in range(0,line):
#		print new_list[new_x]
			
	
#		if ((list_total[line_x][0][0]==list_total[line_x-1][0][0]-3 and line_x>0) or line_x==0):
#			q_tmp += "G0 X" + str(-list_total[line_x][0][0]/zoom) + " Y" + str(-list_total[line_x][0][1]/zoom) + "\n"
#		else :
#			q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][0][0]/zoom) + " Y" + str(-list_total[line_x][0][1]/zoom) + "\n"

#               	for line_y in range (0, len(list_total[line_x])):
#                       	if (line_y%2==0):
#                               	q_tmp += "G0 X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
#                               	q_tmp += "G0 Z"+ z_level_down + "\n"
#                       	else:
#                               	q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
#                               	q_tmp += "G0 Z"+ z_level_up + "\n"

#      		print list_total[line_x]
	q.send(q_tmp)
	q.close()
#	return q_tmp

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
	g = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	gimg=cv2.flip(g,0)
	height, width = gimg.shape
	
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
	
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
#	list_p1 = direction1(gimg,color_level[1],intr0,)
#	list_p2 = direction2(gimg,color_level[2],intr0,)
#	for tx in range (0,167):
	#len() get the size of list
#		for ty in range (0,len(list_p0[0][tx])):
#			print ty
#			if ((list_p0[0][tx][ty][1])>(list_p0[0][tx][ty-1][1]+2) or ty==0):
#				print list_p0[0][tx][ty]
			
#	print list_p0[1]

	p0 = Process(target=dirGCODE,args=(q0,list_p0[0],list_p0[1],zoom,z_level_down,z_level_up,speed,))
#	p1 = Process(target=dirGCODE,args=(q1,list_p1[0],list_p1[1],zoom,z_level_down,z_level_up,speed,))
#	p2 = Process(target=dirGCODE,args=(q2,list_p2[0],list_p2[1],zoom,z_level_down,z_level_up,speed,))
#	p0 = dirGCODE(list_p0[0],list_p0[1],zoom,z_level_down,z_level_up,speed,)
	init_r = dirINIT(height,width,zoom,z_level_down,z_level_up,speed,)
#	list_p2 = direction3(gimg,1,intr0)

	p0.start()
#	p1.start()
#	p2.start()

	q0_r = q0x.recv()
#	q1_r = q1x.recv()
#	q2_r = q2x.recv()	
#	print q0_r
	print("End of Get the Pipe....")

	p0.join()
#	p1.join()
#	p2.join()

	print("Enter the G-code.....")
	filename='painting'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
#	f.write(init_r)
	f.write(q0_r)
#	f.write(q1_r)
#	f.write(q2_r)
#	f.write(list_p2)
	f.write("G0 Z0\rG0 X0 Y0\r")
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
