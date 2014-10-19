import cv2

img = cv2.imread('picture.jpg')

for x in img[0]:
	img[x]=100

cv2.imshow('image',img)
cv2.waitKey(0)
