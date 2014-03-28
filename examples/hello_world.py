from pygios import *
import random
import sys

default_warning(0.5)
default_critical(0.7)

def check():
    value = random.random()
    # yield "Random value is %0.2f" % (value,)
    # yield P("random = %0.8f" % value)

    if value > 0.7:
        critial()
    elif value > warning_threshold():
        warning()


if __name__ == "__main__":
    PygiosMain(sys.argv, check, 'HELLOWORLD')
