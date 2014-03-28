pygios
=========

*A crazy simple python framework that lets you write a Nagios plug in 5
minutes or your money back.*

Building a Nagios plugin should be simple.  Fast.  Easy.  And a some
level it is, all Nagios requires is you return certain error codes,
accept certain command line parameters and format your output in a
certain way, taking care to seperate the two multiplexed streams of
data with Nagios's simple protocol and simple special escaping rules.

Yes, writing a Nagios is easy.  Its just a simple matter of
programming that gets in the way when all you want is to monitor
something and you have 5 minutes in which to do it.

A 5 minute introduction to pygios
=================================

To get started you'll need to install pagios.  {{pip install pygios}}
usually works; if not try {{easy_install pygios}} or try running it as
root as your environmetn might demand.

````bash
pip install pagios 
````

We're going to start by writing a very simple and completely silly
nagios alarm that monitors Python's random number generator.
{{random.randint}} returns floating point numbers between 0 and 1; we
want to receive a warning whenever it generates one larger than 0.5
and a critical alarm when it generates one larger than 0.7.

Now with your favorite editor open up a file called hello_pygios.py.
We start by setting up the {{#!}} preamble and import statements.  We
need a few things from pygios, and access to the command line
arguements and random number generator from {{sys}} and {{random}}
respectively.

````python
#!/usr/bin/env python
# hello_pygios.py

from pygios import check, default_warning, default_critial, PygiosMain
from random import random
from sys import	argv
```` 

Great!   Now continue by adding code to actually perform our test.

```python
def test():
    yield check(random(), "Random value is %0.2f")                               
````

The {{check}} function accepts a value, tests it against the
parameters provided on the command line, and sets the exit code
accordingly.  It also optionally accepts a single message.

Finally we call Pygios' main method to run the test.

````python
if __name__ == "__main__":
    PygiosMain(argv, test, 'HELLOPYGIOS')
````

Now lets try the test on the command line 

````bash
$ python hello_world.py
hello_world.py CRITICAL - Random value is 0.97
$ python hello_world.py
hello_world.py WARNING - Random value is 0.58
$ python hello_world.py
hello_world.py OK - Random value is 0.19
````

... and it works.  




Advanced Tutorial
=================

Together we will create a tool to monitor an SQS queue.  Our tool will
warn when the queue length exceeds 7 and report critial when the queue
length exceeds 10.

Before we can begin, we'll need to setup our enviornment to allow
python to talk to SQS.  By far the most popular tool for this is boto;
if you havn't done so already you should install boto and create an
.boto configuration file for yourself in your home directory.

Boto is pip installable, so you can just type this:

````
pip install boto
````

You should also setup your .boto configuration file.   It looks something like this:

````
aws_access_key_id = AKIAI ....  NA
aws_secret_access_key = Yw0W .... /0
````

Now that you have boto installed, we can setup your AWS account to
support this tutorial by creating an SQS queue.  To do this startup
python and type the following:

````python
>>> import boto.sqs
>>> connection = boto.sqs.connect_to_region('us-east-1')
>>> connection.create_queue('SQS')
Queue(https://queue.amazonaws.com/493123279066/SQS)
````

Now lets create the sqs monitoring script.    First we start with our imports

````python
import boto.sqs
from gflags import FLAGS, DEFINE_string, RegisterValidator
from pygios import P, PygiosMain, default_warning, default_critical, check, more
````

Pygios uses the gflags library instead of optparse.  I recommend you
do too: It has a few features out of the box that optparse doesn't
support like multistrings and makes it really easy to add flags to
modules deep in your stack without the main app needing to know about
it.

This module needs to define two flags for SQS; the queue name and
region.  Defining the region is fairly easy.  The first parameter is
the region name, the second the default, the third the help string.

````python
DEFINE_string('region', 'us-east-1', 'The AWS region to connect.  SQS has seperate namespaces per region')
````

We don't have a sane default for queue name, so use None.  Of course
hte program will crash if we try to use None where a string is
expected, so we might as well move the failure upfront to parameter
passing where it will be obvious.  RegisterValidator is used for this.
The first parmater is the queue name, the second a function that
returns true/false indciating of the parameter passed, and the third
an error messasge to show if the second paramater returns false.


````
DEFINE_string('queue', None, 'The SQS queue name to monitor')
RegisterValidator('queue', lambda x:x is not None, 'You must provide a Queue name')
````

One of the cool things about Gflags is code can register validators
for other modules.  Support your main appliication uses a library in a
way that not all of its potential flags are valid?  No problem,
register a validator.

Central to Nagios are "warning" and "critical" levels; so core are
these that Nagios recomments all plugins use the same parameters -c
and -w for these.  

Pygios provides two methods to do this: {{default__warning}} and
{{default_critical}}.   

````python
default_warning(5)
default_warning(10)
````

It is important to pay attention to the type, because this affects
both the gflags definition behind the scenes and how your values are
compared when the {{check}} method is later called.  Pygios supports
three types; integers, floats and strings.

Now we have to define a method that performs our desired test.  We'll
call this work, but you're free to call it whatever you want.

````python

def work():
    connection = boto.sqs.connect_to_region(FLAGS.region)
````

Here we create a connection to AWS's SQS service and use this
connection to obtain a specific queue and request its length.

````python
    queue = connection.get_queue(FLAGS.queue)
    count = queue.count()
````

Note that if our value in FLAGS.queue doesn't exist, {{get_queue}}
will return a None and {{queue.count}} will fail.  That's okay; if an
exception is raised from within work, Pygios will return UNKNOWN and
exit with an exitcode of 3.

Now that we know the length of the Pygios queue, we can ask pygios to
issue an error code for it based on our thresholds.

````python
    check(count)
````

If your monitor's comparisons are more complicated, pygios exports
methods {{ok}}, {{warning}}, {{critial}}, and {{error}}.  Theses
status related commands may be invoked as many times as desired or not
at all; in absence of an Exception Pygios defaults to OK.  If there
are mulitple invokations Pygios defaults to the hihest numeric value
of all called.

At the very least we'll want to see how long the queue currently is.  To do this:

````python
    yield 'Length is %d' % count
````

Nagios supports 4 levels of verbosity; a command can run with between
zero and three {{-v}} flags respectively.  Pygios supports increasing
degrees of verbosity via the more() command.  Each application of more
"consumes" a {{-v}} flag; when no more exist, the process doesn't
continue forward.  So in this example, the code after {{more()}} will
only be output if there is at least one {{-v}} in the command line
arguements.

````python
    more()
    yield P("length=%d" % (count,))
````

The P object is worth special mention; Nagios supports two streams of
output multiplexed within a single file.  The first stream of output
is the human readable error status.  The second stream is called
"performance data."  This is logged and intended to be machine
parsable for later use.  {{X=Y}} is a common encoding.

So in the above example, we only provide performance data if there is
at least one {{-v}}.

Calling {{more()}} yet again increases the number of {{-v}} required
to emit what follows.  Note that the ordering of {{yield}} statements
between output and performance data doesn't matter; each thread is
output in order with respect to itself, but putting the P and non P
statements before or after one another doesn't affect the behaivor of
the progrma as long as they don't cross more() statements.

````python
    more()
    yield P("queue=%r" % (FLAGS.queue))
    yield 'Queue: %r in AWS region %r' % (FLAGS.queue, FLAGS.region)
    yield P("region=%r" % (FLAGS.region))
````


And finally, we want to make sure our monitor actually runs:

````python
if __name__ == "__main__":
    PygiosMain(work=work)
````

There you have it, an effective SQS length montior.  

````bash
$ python sqs_queue_length.py --name=SQS --queue="pygios"
SQS OK - Length is 0
````
Note how increasing the levels of verbosity affects the output

````bash
$ python sqs_queue_length.py --name=SQS --queue="pygios" -v
SQS OK - Length is 0 | length=0

$ python sqs_queue_length.py --name=SQS --queue="pygios" -v -v
SQS OK - Length is 0 | length=0
Queue: 'pygios' in AWS region 'us-east-1'|queue='pygios'
region='us-east-1'
````

Now lets give sqs_queue_length something to alarm on.  Lets add a few messages from the python consule. 

````python
import boto.sqs
connection = boto.sqs.connect_to_region('us-east-1')
queue = connection.get_queue('pygios')   
from boto.sqs.message import Message
m = Message()
m.set_body('Blab blab')
for _ in range(8): queue.write(m)

````

Now exit the python shell and rerun the sqs_queue_length monitor:

````bash
$ python sqs_queue_length.py --name=SQS --queue="pygios" --region=us-east-1
SQS WARNING - Length is 8
````

Go back into python to add a few more.

````python
import boto.sqs
connection = boto.sqs.connect_to_region('us-east-1')
queue = connection.get_queue('pygios')
from boto.sqs.message import Message
m = Message()
m.set_body('Blab blab')
for _ in range(8): queue.write(m)
````

And back to bash where pygios signals a critial alarm.

````bash
$ python sqs_queue_length.py --name=SQS --queue="pygios" --region=us-east-1
SQS CRITICAL - Length is 16
````

And finally we "process" these jobs by removing them from the system


````python
import boto.sqs
connection = boto.sqs.connect_to_region('us-east-1')
queue = connection.get_queue('pygios')
queue.clear()
````




