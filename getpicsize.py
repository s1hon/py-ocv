import cv2

img = cv2.imread('picture.jpg')
height, width, depth = img.shape

for x in range(height):
	for y in range(width):
		print "%s.%s=%s" %(x,y,img[x][y])

cv2.imshow('image',img)
cv2.waitKey(0)
