import cv2
import numpy as np,sys
import os

print_id= None

#left to right
def writeA(x,y):
	os.system("echo G1 X"+str(x/10)+" Y"+str(y/10)+">>"+print_id)

#mkae filename.nc
def make(pt):
        global print_id
        print_id = str(pt)+'.nc'
        f = open(print_id,'w')
        f.close()

#inport picture
img = cv2.imread('picture.jpg')

#picture to gray
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

make("first")
#G-code basic
os.system("echo G17"+">>"+print_id)
os.system("echo M3 S1000"+">>"+print_id)
os.system("echo G0 X0 Y0"+">>"+print_id)

cv2.imshow('image-before',img)
height, width, depth = img.shape

for x in range(0,height,2):
        for y in range(width):
                if gimg[x][y]<=25 :
                        gimg[x][y]=13
                elif gimg[x][y]<=50 :
                        gimg[x][y]=39
                elif gimg[x][y]<=76 :
                        gimg[x][y]=64
                elif gimg[x][y]<=101 :
                        gimg[x][y]=90
                elif gimg[x][y]<=127 :
                        gimg[x][y]=115
                elif gimg[x][y]<=152 :
                        gimg[x][y]=141
                elif gimg[x][y]<=178 :
                       gimg[x][y]=166
                elif gimg[x][y]<=203 :
                        gimg[x][y]=192
                elif gimg[x][y]<=229 :
                        gimg[x][y]=217
                elif gimg[x][y]<=255 :
                        gimg[x][y]=243
#                print "%s.%s=%s\t%s" %(x,y,img[x][y],gimg[x][y])
#                img[x][y]=gimg[x][y]

		if gimg[x][y]!=243:
			if gimg[x][y-1]!=243:
				writeA(x,y)
			else:
				os.system("echo G0 X"+str(x/10)+" Y"+str((y+1)/10)+">>"+print_id)

	print "%0.1f %%" %((x*100.0)/height)

#cv2.imshow('image-after',img)
cv2.imshow('image-gray',gimg)

cv2.imwrite('./test.jpg',gimg)
cv2.waitKey(0)

