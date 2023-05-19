import unittest
import concurrent.futures as cf
import inspect
from random import choices, randint, random, weibullvariate
from string import ascii_letters, digits, punctuation
from time import sleep, time
from util.concurrent_utils import (
    map_reduce,
    run_concurrent,
    run_procs,
    run_threads
)
from util.stat_utils import pct_diff
from util.timer import Timer


def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


def cpu_worker(task):
    fib(task)
    return task


def concur_worker(params):
    logger, args, task = params
    sleep(task['sleep'])
    if task['raise']:
        raise RuntimeError("concur_worker failed")
    n = randint(task['lower'], task['upper'])
    fib(n)
    return n


def io_worker(task):
    if task is None or task < 0:
        raise ValueError()
    sleep(task)
    return task


def request_worker(params):
    logger, args, task = params
    if task['raise']:
        raise RuntimeError("concur_worker failed")
    logger.info("request_worker sleep for %.3f secs", task['sleep'])
    sleep(task['sleep'])
    rn = randint(task['lower'], task['upper'])
    return choices(ascii_letters + digits + punctuation, k=rn)


def mapper(params):
    args, (key, secs) = params
    ct = randint(20, 33)
    sleep(secs)
    return {key: {int(time() * randint(1000, 9999)): ct}}


def reducer(params):
    args, key, fib_counts = params
    for ct in fib_counts.values():
        fib(ct)
    return len(fib_counts)


class ConcurrentUtilsTest(unittest.TestCase):

    def test_map_reduce_default(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = []
        i_ct = 6
        j_ct = 7
        for i in range(i_ct):
            for j in range(j_ct):
                tasks.append((i, weibullvariate(.2, 1)))
        results, stats = map_reduce(mapper, reducer, tasks)
        self.assertEqual(i_ct, len(results))
        self.assertEqual(i_ct, len([r for r in results if r == j_ct]))
        self.assertEqual(i_ct, stats['map_keys'])
        self.assertEqual(i_ct * j_ct, stats['map_dedup_keys'])

    def test_map_reduce_threads(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = []
        i_ct = 7
        j_ct = 4
        for i in range(i_ct):
            for j in range(j_ct):
                tasks.append((i, weibullvariate(.2, 1)))
        results, stats = map_reduce(mapper, reducer, tasks, m_threads=8)
        self.assertEqual(i_ct, len(results))
        self.assertEqual(i_ct, len([r for r in results if r == j_ct]))
        self.assertEqual(i_ct, stats['map_keys'])
        self.assertEqual(i_ct * j_ct, stats['map_dedup_keys'])

    def test_map_reduce_threads_procs(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = []
        i_ct = 7
        j_ct = 8
        for i in range(i_ct):
            for j in range(j_ct):
                tasks.append((i, weibullvariate(.2, 1)))
        results, stats = map_reduce(
            mapper, reducer, tasks, m_threads=8, r_procs=6)
        self.assertEqual(i_ct, len(results))
        self.assertEqual(i_ct, len([r for r in results if r == j_ct]))
        self.assertEqual(i_ct, stats['map_keys'])
        self.assertEqual(i_ct * j_ct, stats['map_dedup_keys'])

    def test_map_reduce_procs_timeout(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = []
        i_ct = 8
        j_ct = 8
        for i in range(i_ct):
            for j in range(j_ct):
                tasks.append((i, weibullvariate(.2, 1)))
        with self.assertRaises(cf.TimeoutError):
            results, stats = map_reduce(mapper, reducer, tasks, timeout=1)

    def test_run_procs(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [randint(25, 33) for _ in range(50)]
        total_count = 0
        total_results = 0
        for x in run_procs(cpu_worker, tasks, proc_n=5):
            total_count += 1
            total_results += x
        self.assertEqual(len(tasks), total_count)
        self.assertTrue(total_results > 1000)

    def test_run_threads(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [weibullvariate(.5, 1.5) for _ in range(50)]
        total_count = 0
        total_results = 0
        for x in run_threads(io_worker, tasks, thread_n=5):
            total_count += 1
            total_results += x
        self.assertEqual(len(tasks), total_count)
        self.assertTrue(total_results > 10)

    def test_run_threads_timeout(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [.1, .25, .1, .15, .05, .3, 1, .4]
        with self.assertRaises(cf.TimeoutError):
            for x in run_threads(io_worker, tasks, thread_n=3, timeout=1):
                self.assertTrue(x in tasks)

    def test_run_threads_exception(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [.1] * 20 + [-1]
        with self.assertRaises(ValueError):
            for x in run_threads(io_worker, tasks, thread_n=5):
                pass

    def test_run_concurrent_procs(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [{'sleep': random() / 1000,
                  'lower': 20,
                  'upper': 30,
                  'raise': False}
                 for _ in range(100)]
        results1 = []
        with Timer() as tm1:
            for x in run_concurrent(
                    concur_worker, tasks, proc_n=1, thread_n=2):
                results1.append(x)
        results2 = []
        with Timer() as tm2:
            for x in run_concurrent(
                    concur_worker, tasks, proc_n=8, thread_n=2):
                results2.append(x)
        self.assertEqual(len(results1), len(results2))
        pcd = pct_diff(tm1.secs, tm2.secs)
        self.assertTrue(pcd > 50, pcd)

    def test_run_concurrent_threads(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [{'sleep': .05 + random() / 10,
                  'lower': 10,
                  'upper': 20,
                  'raise': False}
                 for _ in range(100)]
        results1 = []
        with Timer() as tm1:
            for x in run_concurrent(
                    concur_worker, tasks, proc_n=2, thread_n=1):
                results1.append(x)
        results2 = []
        with Timer() as tm2:
            for x in run_concurrent(
                    concur_worker, tasks, proc_n=2, thread_n=8):
                results2.append(x)
        self.assertEqual(len(results1), len(results2))
        pcd = pct_diff(tm1.secs, tm2.secs)
        self.assertTrue(pcd > 50, pcd)

    def test_run_concurrent_exception(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [{'sleep': random() / 10, 'lower': 10, 'upper': 28, 'raise': True}
                 for _ in range(20)]
        with self.assertRaises(RuntimeError):
            for x in run_concurrent(concur_worker, tasks, 2, 2):
                print(x)

    def test_run_concurrent_large(self):
        print('-- %s --' % inspect.stack()[0][3])
        tasks = [{'sleep': .02 + random() / 4,
                  'lower': 10,
                  'upper': 28,
                  'raise': False}
                 for _ in range(60000)]
        total_wait = sum([task['sleep'] for task in tasks])
        print("%8s %8s %8s %8s %8s %8s" %
              ('proc_n', 'thread_n', 'count', 'elapsed', 'th_wait', 'work'))
        for proc_n in (3, 5, 8):
            for thread_n in (500, 1000, 2000):
                count = 0
                with Timer() as tm:
                    for x in run_concurrent(
                            request_worker, tasks, proc_n, thread_n):
                        count += len(x)
                print("%8d %8d %8d %8.3f %8.3f %8.3f" %
                      (proc_n, thread_n, count, tm.secs,
                       total_wait / (proc_n * thread_n),
                       total_wait / tm.secs))


if __name__ == '__main__':
    unittest.main()
