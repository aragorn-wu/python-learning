import threading
import time


def target():
    print 'the curent threading  %s is running' % threading.current_thread().name
    time.sleep(1)
    print 'the curent threading  %s is ended' % threading.current_thread().name


print 'the curent threading  %s is running' % threading.current_thread().name
t = threading.Thread(target=target)

t.start()
t.join()
print 'the curent threading  %s is ended' % threading.current_thread().name
