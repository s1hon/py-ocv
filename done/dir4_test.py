import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

def direction3(q,gimg,level):
	q_tmp="G17\nM3 S1000\nG0 X0 Y0\n"
	color = GetLevel(level)
        height, width = gimg.shape
#	width=3
#	height=5
	
	for x in range(height-1,-1,-1):
		for y in range(width-1,-1,-1):		
			if (y==(width-1)) or (y<(width-1) and x==0 ):
 				q_tmp += "G0 X" + str(x) + " Y" + str(y) + "\n"
				tx=x
				ty=y
				print "X %d Y %d" %(tx,ty)
				while(tx+1<height and ty>0) :	
					tx+=1	
					ty-=1
				print "X1 %d Y1 %d" %(tx,ty)      	
				q_tmp += "G1 X" + str(tx) + " Y" + str(ty) + "\n"
				
        
        





#            if gimg[ty][tx]<=color: # black
#                               if (tx+intr<=width and ty+intr<=height) :
#                                        if (gimg[ty+intr][tx+intr]<=color or tx==0): # white || y=0
#                                                q_tmp += "G1 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
#                                        elif ty==height: # if y has gone end.
#                                                q_tmp += "G0 X" + str(tx/zoom) + " Y" + str(ty/zoom) + "\n"
#                        elif (tx-intr>width and ty-intr>height) :
#                                if (gimg[tx+intr][ty+intr]<=color and ty>0): # black && y > 0
                                #    q_tmp += "G0 X" + str(tx/zoom) + " Y" + str((ty-1)/zoom) + "\n"
                #        tx+=intr
                 #       ty+=intr
	q.send(q_tmp)
       	q.close
       	print("d3 DONE!")



def GetLevel(level):
        if level == 1 :
                return 223
        elif level == 2 :
                return 191
        elif level == 3 :
                return 159
        elif level == 4 :
                return 127
        elif level == 5 :
                return 95
        elif level == 6 :
                return 63
        elif level == 7 :
                return 31
if __name__ == '__main__':
        #pic to gray
        gimg = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	


	q3x,q3 = Pipe()
	p3 = Process(target=direction3,args=(q3,gimg,1))

	p3.start()
	q3_r = q3x.recv()
	print("End of Get the Pipe....")

	p3.join()
        print("p3 end!")

	print("Make the file.....")
        filename='t127'
        file_id = str(filename) + '.nc'
        f = open(file_id,'w')
 	f.write(q3_r)
        f.close()















