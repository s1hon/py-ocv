import cv2
import numpy as np,sys
img = cv2.imread('picture.jpg')
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

cv2.imshow('image-before',img)
height, width, depth = img.shape

for x in range(height):
	for y in range(width):
		if gimg[x][y]<=25 :
			gimg[x][y]=13
		if gimg[x][y]<=50 and gimg[x][y] >=26:
			gimg[x][y]=39
		if gimg[x][y]<=76 and gimg[x][y] >=51 :
			gimg[x][y]=64
		if gimg[x][y]<=101 and gimg[x][y] >=77 :
			gimg[x][y]=90
		if gimg[x][y]<=127 and gimg[x][y] >=102 :
			gimg[x][y]=115
		if gimg[x][y]<=152 and gimg[x][y] >=128 :
			gimg[x][y]=141
		if gimg[x][y]<=178 and gimg[x][y] >=153 :
			gimg[x][y]=166
		if gimg[x][y]<=203 and gimg[x][y] >=179 :
			gimg[x][y]=192
		if gimg[x][y]<=229 and gimg[x][y] >=204 :
			gimg[x][y]=217
		if gimg[x][y]<=255 and gimg[x][y] >=230 :
			gimg[x][y]=243
		print "%s.%s=%s\t%s" %(x,y,img[x][y],gimg[x][y])
		img[x][y]=gimg[x][y]

#cv2.imshow('image-after',img)
cv2.imshow('image-gray',gimg)

cv2.waitKey(0)
