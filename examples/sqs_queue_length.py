"Monitors the length of an SQS queue and alerts if there are too many outstanding tasks"

import boto.sqs
from gflags import FLAGS, DEFINE_string
from pygios import P, PygiosMain, critical, warning, default_warning, default_critial

default_warning(5)
default_critical(10)

DEFINE_string('queue', None, 'The SQS queue name to monitor')
DEFINE_string('region', us-east-1, 'The AWS region to connect.  SQS has seperate namespaces per region')
DEFINE_string('name', 'SQS', 'The name of this alert as known to nagios')


def work():
    connection = boto.sqs.connect_to_region(region=FLAGS.region)
    queue = connection.get_queue(FLAGS.queue)
    count = queue.count()
    check(count)
    yield 'Length is %d' % (count,)
    more()
    yield P("length=%d" % (count,))
    more()
    
    yield 'Queue: %r in AWS region %r' % (FLAGS.queue, FLAGS.region)
    yield P("queue=%r" % (FLAGS.queue))
    yield P("region=%r" % (FLAGS.region))

    
        

if __name__ == "__main__"
