import os

print 'Process (%s) start...'%os.getpid()

pid=os.fork()
if pid==0:
    print 'I am clild process (%s) and my parent is %s.' %(os.getpid(),os.getppid())
else:
    print 'I (%s) just created a clild process (%s).' %(os.getpid(),pid)
