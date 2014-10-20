import cv2
import numpy as np,sys

img = cv2.imread('icon-10x10-twitter.png')
gimg = cv2.imread('icon-10x10-twitter.png',cv2.IMREAD_GRAYSCALE)

cv2.imshow('image-before',img)
height, width, depth = img.shape
print width,height
for x in range(height):
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
                print "%s\t" %(gimg[x][y]),
                img[x][y]=gimg[x][y]
	print ""	

#cv2.imshow('image-after',img)
cv2.imshow('image-gray',gimg)

cv2.waitKey(0)

