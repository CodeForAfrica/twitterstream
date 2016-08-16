#!/usr/bin/env python
import os
import pika
from daemon import Daemon
from threading import Thread
from tools import ThreadPool
from pika.adapters import SelectConnection
from logging.handlers import TimedRotatingFileHandler

import traceback
import logging,os,sys
from logging.handlers import TimedRotatingFileHandler

import datetime
from datetime import datetime as dt

from twitterstream import config

def _log(resources={}, msg="", level="debug"):
    if "logger" in resources:
        eval("resources['logger'].%s(msg)" % level)
    else:
        print msg

class Consumer(object):
    def __init__(self,id,resources):
        queue_name = config.RABBITMQ["queue"]
        self.connection = None
        self.channel = None
        self.response = None
        self.consumerId = 'thread:%d' %(id,)
        self.logger = resources['logger']
        self.resources = resources
        self.queue = queue_name

    def handle_delivery(self,channel,method,header,body):
        try:
            msg = str(body).strip()
            self.logger.info("Consumed: %s" % msg)

        except Exception,e:
            try:
                self.logger.error('op:handleDelivery, '
                        'status:failed to process_provision_'
                        'response, msg: %s, error: %s' % (
                            message, str(e)))
                self.logger.error(traceback.format_exc())
            except Exception:
                pass

    def on_queue_declared(self,frame):
        self.logger.debug('... declaring queue')
        self.channel.basic_qos(prefetch_count =1)
        try:
            self.channel.basic_consume(self.handle_delivery,queue=self.queue,no_ack=True)
        except Exception,e:
            self.logger.error('crashing')

    def on_channel_open(self,channel):
        self.channel = channel
        try:
            self.channel.queue_declare(queue=self.queue,exclusive=False,durable=True,auto_delete=False,callback=self.on_queue_declared)
        except Exception,e:
            logger.error(str(e),)

    def on_connected(self,connection):
        connection.channel(self.on_channel_open)

    def consume(self,):
        try:
            from pika.adapters import SelectConnection
            #self.connection = SelectConnection(pika.ConnectionParameters(host='127.0.0.1'),self.on_connected)

            self.connection = SelectConnection(pika.ConnectionParameters(
                host=config.RABBITMQ["host"],
                virtual_host=config.RABBITMQ["vhost"],
                credentials=pika.credentials.PlainCredentials(
                    username=config.RABBITMQ["credentials"].split(",")[0],
                    password=config.RABBITMQ["credentials"].split(",")[1])),
                self.on_response_connected)
            self.logger.debug("connected...")

            self.connection.ioloop.start()
        except Exception,e:
            self.connection.close()
            self.connection.ioloop.start()
        else:
            pass


def setup(log):
    '''defines resources
    '''
    try:
        print "here"
        cwd = os.getcwd()
        resources = {}
        logger = logging.getLogger(log)
        logger.setLevel(logging.DEBUG)
        ch = TimedRotatingFileHandler('%s/logs/%s.log' %(cwd,log,),'midnight')
        print cwd, log
        print "*" * 40
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        resources['logger'] = logger
    except Exception,e:
        logger.error(str(e))
        sys.exit(2)
    else:
        return resources


class Dequeue(Daemon):
    def __init__(self,pidfile):
        self.resources = None
        self.logger = None
        super(Dequeue,self).__init__(pidfile)

    def run(self):
        workers = 5
        self.resources = setup('log-consumer')
        self.logger = self.resources['logger']
        self.logger.debug("TEST ======")
        pool = ThreadPool(workers,self.logger)
        self.logger.info('adding workers to pool')
        for i in range(1,(workers+1)):
            pool.add_task(Consumer(i,self.resources).consume)
        try:
            self.logger.info('added threads to pool')
            pool.wait_completion()
        except Exception,e:
            self.logger.error('died')

if __name__ == '__main__':
    import sys
    cwd = os.getcwd()
    daemon = Dequeue('%s/consumer.pid' %(cwd))
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print 'dequeue daemon starting ....'
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print 'dequeue daemon stopping .....'
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print 'dequeue daemon restarting ....'
            daemon.restart()
        else:
            print "unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" %sys.argv[0]
        sys.exit(2)

