import os
import cv2
import numpy as np,sys
print_id= None

def writeA(x1,y1):
	if print_id  :
		os.system("echo G17"+" >> "+ print_id)
		os.system("echo M3 S1000"+" >> "+ print_id)
		os.system("echo G0 X" +x1+" Y"+y1+ " >> "+ print_id)
		for x in range(10) :
			os.system("echo G1 X0"+" Y"+ str(x+1) + " >> "+ print_id)
			os.system("echo G1 X"+ str(x+1) +" Y0"+ " >> "+ print_id)	
		while x>=0 :
			x-=1
			os.system("echo G1 X0"+" Y"+ str(x+1) + " >> "+ print_id)
			os.system("echo G1 X"+ str(x+1) +" Y0"+ " >> "+ print_id)	
	else :
		print("err")

def make(pt):
	global print_id
	print_id = str(pt)+'.nc'
	f = open(print_id,'w')
	f.close()


def show(pn):
	global pic_id
	pic_id = str(pn)+'.jpg'
	gimg = cv2.imread(pic_id)
	cv2.imshow('image',gimg)
	height, width, depth = gimg.shape

	for x in range(height):
        	for y in range(width):
			os.system("echo x" + "  >> " + pic_file)

	cv2.waitKey(0)

def showfile(sf):
	global pic_file
	pic_file = str(sf)+'.nc'
	f = open(pic_file,'w')
	f.close()
		
