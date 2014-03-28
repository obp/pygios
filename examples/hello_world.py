from pygios import check, default_warning, default_critical, PygiosMain
from random import random 
from sys import argv

default_warning(0.5)
default_critical(0.7)

def test():
    yield check(random(), "Random value is %0.2f")


if __name__ == "__main__":
    PygiosMain(argv, test, 'HELLOPYGIOS')
