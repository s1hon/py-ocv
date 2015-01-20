import os

cy=0
for x in range(5):
	os.system("echo G0 X" + str(x) + " Y" + str(cy) + ">>" + test.nc)
	for y in range(5):
		if y==3:
			os.system("echo G1 X" + str(x) + " Y" + str(y) + ">>" + test.nc)
		elif y>3:
			os.system("echo G0 X" + str(x) + " Y" + ">>" + test.nc)
			
