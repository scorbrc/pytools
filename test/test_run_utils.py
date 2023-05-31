import unittest
import dateutil.parser as dp
import inspect
from random import randint, weibullvariate
from time import sleep, time
from util.run_utils import ConcurrentRunner
from util.run_utils import run_concurrent
from util.run_utils import run_singleton, run_subproc


def args_worker(args, task):
    if task is None:
        raise RuntimeError()
    fib(task)
    sleep(weibullvariate(args['a'], .5))
    return task


def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


def cpu_worker(task):
    fib(task)
    return task


def io_worker(task):
    sleep(task)
    return task


def co_num(params):
    co, n = params
    return co.increment(n)


def xtest_singleton(params):
    name, secs = params
    sleep(secs)
    result = run_singleton(name)
    return result


class RunUtilsTest(unittest.TestCase):

    def xtest_run_singleton(self):
        print(inspect.stack()[0][3])
        ct = 0
        with ConcurrentRunner.procs(2) as cr:
            for rslt in cr.run_collect(test_singleton, [('p', .5), ('p', .1)]):
                if rslt:
                    ct += 1
        self.assertEqual(1, ct)

    def xtest_run_subproc(self):
        print(inspect.stack()[0][3])
        out = run_subproc("date")
        self.assertTrue(len(out) > 0)
        dp.parse(out)

    def xtest_run_subproc_input(self):
        print(inspect.stack()[0][3])
        out = run_subproc("grep token", "first\nthe token\nlast")
        self.assertEqual('the token', out)

    def xtest_run_subproc_fail(self):
        print(inspect.stack()[0][3])
        with self.assertRaises(RuntimeError):
            run_subproc("bad")

    def xtest_run_concurrent_functions_01(self):
        print(inspect.stack()[0][3])
        with ConcurrentRunner.threads() as cr:
            for i in range(10):
                cr.run(lambda x: x * 2, i + 1)
        x = sorted(list(cr.collect()))
        self.assertEqual([2, 4, 6, 8, 10, 12, 14, 16, 18, 20], x)

    def xtest_run_concurrent_functions_02(self):
        print(inspect.stack()[0][3])
        with ConcurrentRunner.threads() as cr:
            x = sorted(list(
                cr.run_collect(lambda x: x * 2, list(range(1, 11)))))
        self.assertEqual([2, 4, 6, 8, 10, 12, 14, 16, 18, 20], x)

    def xtest_run_concurrent_cpu_worker_01(self):
        print(inspect.stack()[0][3])
        st = time()
        with ConcurrentRunner.procs(3) as cr:
            for _ in range(12):
                cr.run(cpu_worker, 27)
            list(cr.collect())
        t1 = time() - st
        st = time()
        with ConcurrentRunner.threads(3) as cr:
            for _ in range(12):
                cr.run(cpu_worker, 27)
            list(cr.collect())
        t2 = time() - st
        rpt = "t1=%.3f, t2=%.3f pd=%.3f" % (t1, t2, t2 / t1)
        self.assertTrue(t2 / t1 > 1, rpt)

    def xtest_run_concurrent_cpu_worker_02(self):
        print(inspect.stack()[0][3])
        fts = []
        with ConcurrentRunner.procs(3) as cr:
            for _ in range(12):
                fts.append(cr.run(cpu_worker, 25))
        for ft in fts:
            self.assertTrue(ft.done())

    def xtest_run_concurrent_io_worker_01(self):
        print(inspect.stack()[0][3])
        st = time()
        with ConcurrentRunner.threads(3) as cr:
            for _ in range(12):
                cr.run(io_worker, .5)
        t1 = time() - st
        st = time()
        with ConcurrentRunner.procs(3) as cr:
            for _ in range(12):
                cr.run(io_worker, .5)
        t2 = time() - st
        pd = abs((t2 - t1) / ((t2 + t1) / 2))
        rpt = "t1=%.3f, t2=%.3f pd=%.3f" % (t1, t2, pd)
        self.assertTrue(pd < .5, rpt)

    def xtest_run_concurrent_io_worker_02(self):
        print(inspect.stack()[0][3])
        fts = []
        with ConcurrentRunner.procs(3) as cr:
            for _ in range(20):
                fts.append(cr.run(io_worker, .5))
        for ft in fts:
            self.assertTrue(ft.done())

    def xtest_run_concurrent_io_pipeline(self):
        print(inspect.stack()[0][3])
        st = time()
        t = 3
        c = 12
        w = .5
        with ConcurrentRunner.threads(t) as cr1:
            for _ in range(12):
                cr1.run(io_worker, w)
            with ConcurrentRunner.threads(t) as cr2:
                for x in cr1.collect():
                    cr2.run(io_worker, x)
        x = time() - st
        y = c / t * w
        rpt = "x=%.3f y=%.3f: %.3f" % (x, y, x / y)
        self.assertTrue(x / y < 2, rpt)

    def test_run_concurrent(self):
        print(inspect.stack()[0][3])
        args = {'a': .05}
        tasks = [randint(20, 33) for _ in range(200)]
        total = 0
        for x in run_concurrent(args_worker, args, tasks, procs=4, threads=4):
            total += x
        self.assertEqual(sum(tasks), total)

    def test_run_concurrent_cpu(self):
        print(inspect.stack()[0][3])
        args = {'a': 0}
        tasks = [randint(20, 33) for _ in range(200)]
        total = 0
        for x in run_concurrent(args_worker, args, tasks, procs=1, threads=10):
            total += x
        self.assertEqual(sum(tasks), total)

    def test_run_concurrent_io(self):
        print(inspect.stack()[0][3])
        args = {'a': .05}
        tasks = [1] * 100
        total = 0
        for x in run_concurrent(args_worker, args, tasks, procs=1, threads=10):
            total += x
        self.assertEqual(sum(tasks), total)


if __name__ == '__main__':
    unittest.main()
