import cv2

img = cv2.imread('picture.jpg')
gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)

height, width, depth = img.shape

for x in range(height):
	for y in range(width):
		print "%s.%s=%s\t%s" %(x,y,img[x][y],gimg[x][y])
		img[x][y]=gimg[x][y]

cv2.imshow('image',img)
cv2.imshow('image-gray',gimg)

cv2.waitKey(0)
