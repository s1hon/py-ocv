def my_function(q,x):
    print q ,x, '100'

def call_me():
    p = Process(target=my_function, args=('x','y'))
    p.start()
    p.join() # this blocks until the process terminates
    # result = queue.get()
    # print result
    return