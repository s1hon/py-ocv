import cv2
import numpy as np,sys
import os

gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
height, width = gimg.shape

for x in range(height):
	for y in range(width):
		print "[%s][%s]=%s" %(x,y,gimg[x][y])

cv2.imshow("gray",gimg)
cv2.waitKey(0)
