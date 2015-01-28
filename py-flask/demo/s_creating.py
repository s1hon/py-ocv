from multiprocessing import Process
import time

def my_function(print_id):
    time.sleep(5)
    g.db.execute('update prints set status="1" where print_id="'+print_id+'"')
    g.db.commit()
    app.logger.info('[Gcode] Creating Done <PID:'+print_id+'>')


# if __name__ == '__main__':
#     p = Process(target=my_function, args=('x','y'))
#     p.start()
#     p.join() # this blocks until the process terminates
#     # result = queue.get()
#     # print result