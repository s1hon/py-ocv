import os

print_id= None

def writeA(ss):
	if print_id  :
		os.system("echo " +ss+ " >> "+ print_id)
	else :
		print("err")

def make(pt):
	global print_id
	print_id = str(pt)+'.nc'
	f = open(print_id,'w')
	f.close()

