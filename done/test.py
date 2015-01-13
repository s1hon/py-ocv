import os
import time

def child():
	print 'A new child ',os.getpid()
	os._exit(0)

while True:
	newpid=os.fork()
	if newpid==0:
		child()
	else:
		pids=(os.getpid(),newpid)
		print "parent:%d,child:%d" %pids
	time.sleep(1)
	break;

 
