import unittest
from StringIO import StringIO
from pygios import PygiosMain, reset, warning, critical, P, more
from gflags import FLAGS


class PygiosTestCase(unittest.TestCase):
    name = 'changeme'
    def setUp(self):
        reset()
        self.exits = []
        self._stdout = StringIO()
        self.exitcode = PygiosMain(args=[self.name],
                                   work=self.work,
                                   stdout=self._stdout,
                                   exit=lambda x:x)

        self.stdout = self._stdout.getvalue()

    def work(self):
        pass


    def tearDown(self):
        reset()

    def test_name_in_output(self):
        self.assertIn(self.name, self.stdout)


class PygiosZeroVerbosity(PygiosTestCase):

    @property
    def name(self):
        return "VERBOSITY_TEST_%d" % (self.LEVEL)

    def work(self):
        yield "zero"
        more()
        yield "one"
        more()
        yield "two"
        more()
        yield "three"

    def setUp(self):
        self._verbose = FLAGS.verbose 
        FLAGS.verbose = self.LEVEL
        PygiosTestCase.setUp(self)

    def tearDown(self):
        PygiosTestCase.tearDown(self)
        FLAGS.verbose = self._verbose

    LEVEL = 0 

    def test_zero(self):
        self.assertIn('zero', self.stdout)

    def test_one(self):
        self.assertNotIn('one', self.stdout)
        
    def test_two(self):
        self.assertNotIn('two', self.stdout)
        
    def test_three(self):
        self.assertNotIn('three', self.stdout)
        

class PygiosOneVerbosity(PygiosZeroVerbosity):
    LEVEL = 1 
    def test_one(self):
        self.assertIn('one', self.stdout)
        
        
class PygiosTwoVerbosity(PygiosOneVerbosity):
    LEVEL = 2 
    def test_two(self):
        self.assertIn('two', self.stdout)

class PygiosThreeVerbosity(PygiosTwoVerbosity):
    LEVEL = 3 
    def test_three(self):
        self.assertIn('three', self.stdout)
        
        

class PygiosEmptyTest(PygiosTestCase):

    name = "foobar"
    def work(self):
        pass

    def test_is_ok(self):
        "confirm test result has string OK"        
        self.assertIn('OK', self.stdout)

    def test_is_not_warning(self):
        self.assertNotIn('WARNING', self.stdout)

    def test_is_not_critial(self):
        self.assertNotIn('CRITICAL', self.stdout)

    def test_lines(self):
        self.assertEquals(len(filter(None, self.stdout.split('\n'))),
                          1)


class PygiosWarningTest(PygiosTestCase):

    name = "foobar"
    def work(self):
        warning()

    def test_is_not_ok(self):
        "confirm test result has string OK"        
        self.assertNotIn('OK', self.stdout)

    def test_is_warning(self):
        self.assertIn('WARNING', self.stdout)

    def test_is_not_critial(self):
        self.assertNotIn('CRITIAL', self.stdout)

    def test_lines(self):
        self.assertEquals(len(filter(None, self.stdout.split('\n'))),
                          1)


class PygiosCriticalTest(PygiosTestCase):

    name = "foobar"
    def work(self):
        critical()

    def test_is_notgood(self):
        "confirm test result has string OK"        
        self.assertNotIn('OK', self.stdout)

    def test_is_not_warning(self):
        self.assertNotIn('WARNING', self.stdout)

    def test_is_critial(self):
        self.assertIn('CRITICAL', self.stdout)

    def test_output(self):
        self.assertEquals(self.stdout, 'foobar CRITICAL - \n')


if __name__=="__main__":
    unittest.main()
