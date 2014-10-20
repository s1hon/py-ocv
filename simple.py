import os,time


def writeA(ss,pt):
	print_id = make(pt)

	print "print_id="+print_id

	if print_id  :
		os.system("echo " +ss+ " >> "+ print_id +".nc")
	else :
		print("err")

def make(pt):
	f = open(pt,'w')
	f.close()
	return pt

writeA("aa","4a139017")
