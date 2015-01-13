import os

def child():
	print 'A new child', os.getpid()
	os._exit(0)

def parent():
	while True:
		newpid = os.fork()
		if newpid == 0:
			child()
		else:
			pids = (os.getpid(),newpid)
			print"parent: %d child: %d" %pids
		if raw_input() == 'exit': break
parent()
