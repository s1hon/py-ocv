import cv2
import numpy as np,sys

img = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

#----------------------------------------------------------------------
# Reference http://opencvpython.blogspot.tw/2013/05/thresholding.html |
#----------------------------------------------------------------------
# threshold parameters [cv2.THRESH_BINARY,cv2.THRESH_BINARY_INV,      |
#		        cv2.THRESH_TRUNC,cv2.THRESH_TOZERO,           |
#		        cv2.THRESH_TOZERO_INV]                        |
#----------------------------------------------------------------------

ret,thresh1 = cv2.threshold(img,223,255,cv2.THRESH_BINARY)
ret,thresh2 = cv2.threshold(img,223,255,cv2.THRESH_BINARY_INV)
#ret,thresh3 = cv2.threshold(img,127,255,cv2.THRESH_TRUNC)
#ret,thresh4 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO)
#ret,thresh5 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)


cv2.imshow("img",img)
cv2.imshow("1",thresh1)
cv2.imshow("2",thresh2)
cv2.imshow("3",thresh3)
cv2.imshow("4",thresh4)
cv2.imshow("5",thresh5)
cv2.waitKey(0)
