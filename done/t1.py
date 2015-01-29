import time
import os
from multiprocessing import Process, Queue
def f(q1):
	q1.put([11, 'hello'])
def ff(q2):
	q2.put([222222])	
if __name__ == '__main__':
	q1 = Queue()
	q2 = Queue()
	p1 = Process(target=f, args=(q1,))
	p2 = Process(target=ff, args=(q2,))
	p1.start()
	p2.start()
	print q1.get()
	print q2.get()
	p1.join()
	p2.join()

