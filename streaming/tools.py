#import xmlrpclib2
import httplib
import datetime
from datetime import tzinfo,timedelta
import re
import logging
import sys, os
from Queue import Queue
from threading import Thread

logger = logging.getLogger( 'airhandler.tools' )

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                print 'running'
                func(*args, **kargs)
            except Exception, e:
                print 'choking'
            else:
                try:
                    self.tasks.task_done()
                except Exception,e:
                    print 'done'
                else:
                    print 'completed'

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads,lg):
        self.logger = lg
        self.logger.info('creating queue')
        self.tasks = Queue(num_threads)
        self.logger.info('created queue')
        
        for _ in range(num_threads):
            self.logger.info('added tasks')
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        try:
            self.tasks.put((func, args, kargs))
        except Exception,e:
            self.logger.error('error creating worker threads %s' %(str(e)))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        try:
            self.tasks.join()
        except Exception,e:
            self.logger.error('error waiting completion %s' %(str(e),))

def daemonize (stdout='/dev/null', stderr='/dev/null',pidfile='daemon.pid',stdin='/dev/null'):
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
           # pidFile = open(pidfile,'w')
           # pidFile.write(str(pid))
           # pidFile.close()
            sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)    )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            pidFile = open(pidfile,'w')
            pidFile.write(str(pid))
            pidFile.close()

            sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror)    )
        sys.exit(1)

    # Now I am a daemon!
    sys.stdin = open(stdin, 'r')
    sys.stdout = open(stdout, 'a')
    sys.stderr = open(stderr, 'a')
