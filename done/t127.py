import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe


#direction top to bottom
def direction0(q,gimg):
	height, width = gimg.shape
	intr=5
	zoom=20.0
	q_tmp="G17\nM3 S1000\nG0 X0 Y0\n"
	for x in range(0,height,intr):
		for y in range(width):
			if gimg[x][y]<=223: # black
				if (gimg[x][y-1]>223 or y==0): # white || y=0
					q_tmp += "G0 X" + str(x/zoom) + " Y" + str(y/zoom) + "\n"
				elif y==(width-1): # if y has gone end.
					q_tmp += "G1 X" + str(x/zoom) + " Y" + str(y/zoom) + "\n"
			elif (gimg[x][y-1]<=223 and y>0): # black && y > 0
				q_tmp += "G1 X" + str(x/zoom) + " Y" + str((y-1)/zoom) + "\n"
	q.send(q_tmp)
	q.close
	print("d0 DONE!")

def direction1(q,gimg):
	height, width = gimg.shape
	q_tmp=''
	intr=5
	zoom=20.0
	for y in range(0,width,intr):
		for x in range(height):
			if gimg[x][y]<=191: # black
				if (gimg[x-1][y]>191 or x==0): # white || y=0
					q_tmp += "G0 X" + str(x/zoom) + " Y" + str(y/zoom) + "\n"
				elif x==(height-1): # if y has gone end.
					q_tmp += "G1 X" + str(x/zoom) + " Y" + str(y/zoom) + "\n"
			elif (gimg[x-1][y]<=191 and x>0): # black && y > 0
				q_tmp += "G1 X" + str((x-1)/zoom) + " Y" + str(y/zoom) + "\n"
	q.send(q_tmp)
	q.close
	print("d1 DONE!")


def direction2(q,gimg):
	height, width = gimg.shape
	q_tmp=''
	intr=5
	zoom=20.0
	the_range=[]

	for x in range(height-1,0,-intr):
		the_range.append([x,0])
	for y in range(0,width,intr):
		the_range.append([0,y])
	print(the_range)
	for t_range in the_range:
		print t_range
		tx=t_range[0]
		ty=t_range[1]
		q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
		print "X %d Y %d" %(tx,ty)
		while (tx>=0 and tx+intr<height and ty>=0 and ty+intr<width ):
			print "X1 %d Y1 %d" %(tx,ty)
			if gimg[tx][ty]<=159: # black
				if (tx+intr<=height and ty+intr<=width) :
					if (gimg[tx+intr][ty+intr]<=159 or ty==0): # white || y=0
						q_tmp += "G1 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
					elif ty==width: # if y has gone end.
						q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
			elif (tx+intr<height and ty+intr<width) :
				if (gimg[tx+intr][ty+intr]<=159 and ty>0): # black && y > 0
					q_tmp += "G0 X" + str(tx/zoom) + " Y" + str((ty-1)/zoom) + "\n"
			tx+=intr
			ty+=intr

	q.send(q_tmp)
	q.close
	print("d2 DONE!")




if __name__ == '__main__':
	#pic to gray
	gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	p0 = Process(target=direction0,args=(q0,gimg,))
	p1 = Process(target=direction1,args=(q1,gimg,))
	p2 = Process(target=direction2,args=(q2,gimg,))
	p0.start()
	p1.start()
	p2.start()

	q0_r = q0x.recv()
	q1_r = q1x.recv()
	q2_r = q2x.recv()
	print("End of Get the Pipe....")

	p0.join()
	print("p0 end!")

	p1.join()
	print("p1 end!")

	p2.join()
	print("p1 end!")

	print("Make the file.....")
	filename='t127'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(q0_r+q1_r+q2_r)
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
