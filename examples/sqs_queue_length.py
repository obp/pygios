"""Monitors the length of an SQS queue and alerts if there are too
many outstanding tasks"""

import boto.sqs
from gflags import FLAGS, DEFINE_string, RegisterValidator
from pygios import P, PygiosMain, critical, warning, default_warning, default_critical, check, more


DEFINE_string('queue', None, 'The SQS queue name to monitor')
DEFINE_string('region', 'us-east-1', 'The AWS region to connect.  SQS has seperate namespaces per region')
RegisterValidator('queue', lambda x:x is not None, 'You must provide a Queue name')


# Just a note to new sysadmins: Nagios shouldn't do anything unless
# the system requires manual intervention.  The difference between a
# warning and a critical is whether or not the problem is customer
# visible.  When setting these thresholds try to avoid the 70% rule
# nagios recommends.  You should set these values to whatever
# inidicates your system is broken in a way that you must fix
# manually.  Warnings that you cannot act on just disrupt your
# weekend.

default_warning(5)
default_critical(10)


def work():
    connection = boto.sqs.connect_to_region(FLAGS.region)
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


if __name__ == "__main__":
    PygiosMain(work=work)
