"""
Functions for running processes and threads.

map_reduce for running data with keys through a two-stage processes.
run_procs for running multiple processes
run_threads for running multiple threads
run_concurrent for running multiple processes with each process also running
multiple threads.

"""
from collections import defaultdict
import concurrent.futures as cf
import sys
from time import perf_counter
from util.logging_utils import get_logger
from util.util_tools import flatten_list

MR_PROC_N = 5


def map_reduce(mapper_fn, reducer_fn, tasks,
               args={},
               m_procs=None,
               m_threads=None,
               r_procs=None,
               r_threads=None,
               timeout=900):
    """
    Map/reduce as a two-stage process for concurrently executing tasks.
    Mappers process tasks into dictionaries of mapping keys to dictionaries
    of dedup keys/values to ensure a unique set of data passed to the reducers.
    'mapper_fn' mapper function that accepts 'args' passed through and one
    of the 'tasks' and returns {map_key:{dedup_key:value}}.
    'reducer_fn' reducer function that accepts 'args' passed through and a
    dictionary of dedup keys and values.
    'tasks' list of tasks for mapper function to process.
    Optional arguments:
    'args' passed to each call of 'mapper_fn' and each call of 'reducer_fn'.
    'm_procs' create process pool for the mappers with process count.
    'm_threads' create thread pool for the mappers with this thread count.
    'r_procs' create process pool for the reducers with this process count.
    'r_threads' create thread pool for the reducers with this thread count.
    'timeout' maximum seconds to run mapping phase and reducing phase.
    If reducer not specified then it will use the mapper pool. If mapper
    not specified then default is to use a process pool with five processes.
    """
    if m_procs is not None:
        m_pool = cf.ProcessPoolExecutor(max_workers=m_procs)
    elif m_threads is not None:
        m_pool = cf.ThreadPoolExecutor(max_workers=m_threads)
    else:
        m_pool = cf.ProcessPoolExecutor(max_workers=MR_PROC_N)
    if r_procs is not None:
        r_pool = cf.ProcessPoolExecutor(max_workers=r_procs)
    elif r_threads is not None:
        r_pool = cf.ThreadPoolExecutor(max_workers=r_threads)
    else:
        r_pool = m_pool
    try:
        st = perf_counter()
        stats = {}
        parts = defaultdict(dict)
        task_args = [(args, task) for task in tasks]
        for recs in m_pool.map(mapper_fn, task_args, timeout=timeout):
            for mk, dd in recs.items():
                for dk, v in dd.items():
                    parts[mk][dk] = v
        stats['map_keys'] = len(parts)
        stats['map_dedup_keys'] = sum([len(parts[mk]) for mk in parts])
        stats['map_secs'] = perf_counter() - st
        st = perf_counter()
        rds = [(args, mk, dd) for i, (mk, dd) in enumerate(parts.items())]
        results = list(r_pool.map(reducer_fn, rds, timeout=timeout))
        stats['reduce_secs'] = perf_counter() - st
        return flatten_list(results), stats
    except KeyboardInterrupt:
        print('Terminating...')
        sys.exit(1)


def run_worker_tasks(executor, worker_tasks, concur_n=4, timeout=300):
    """
    Runs function 'worker_tasks', a list of worker functions and tasks
    in executor with 'concur_n' number of threads or processes.
    Each worker function will take one of the tasks in its list and produce
    a result that will be returned to the client. Worker functions might also
    return an id so the client can tell what produced the results. Wait for
    up to 'timeout' seconds for results to be produced. Any exceptions thrown
    are forwarded to the client.
    """
    with executor(max_workers=concur_n) as executor:
        futures = set()
        for worker, task in worker_tasks:
            futures.add(executor.submit(worker, task))
        try:
            for ft in cf.as_completed(futures, timeout):
                if ft.exception() is not None:
                    raise ft.exception()
                yield ft.result()
        except KeyboardInterrupt:
            print('Terminating...')
            sys.exit(1)


def run_procs(worker, tasks, proc_n=4, timeout=300):
    """
    Runs function 'worker' on 'proc_n' number of processes. The 'worker'
    function must take one of the 'tasks' and produce a result that will be
    returned to the client. 'timeout' is the number of seconds to wait for
    results to be produced. Any exceptions thrown are forwarded to the client.
    """
    worker_tasks = [(worker, task) for task in tasks]
    return run_worker_tasks(cf.ProcessPoolExecutor, worker_tasks, proc_n, timeout)


def run_procs_worker_tasks(worker_tasks, proc_n=4, timeout=300):
    """
    Runs function 'worker_tasks', a dictionary of worker functions to lists
    of tasks on 'proc_n' number of processes. Each worker function will take
    one of the tasks in its list and produce a result that will be
    returned to the client. Worker functions might also return an id so the
    client can tell what produced the results. Wait for up to 'timeout'
    seconds for results to be produced. Any exceptions thrown are forwarded
    to the client.
    """
    return run_worker_tasks(cf.ProcessPoolExecutor, worker_tasks, proc_n, timeout)


def run_threaded_worker_tasks(worker_tasks, thread_n=4, timeout=300):
    """
    Runs function 'worker_tasks', a dictionary of worker functions to lists
    of tasks on 'thread_n' number of threads. Each worker function will take
    one of the tasks in its list and produce a result that will be
    returned to the client. Worker functions might also return an id so the
    client can tell what produced the results. Wait for up to 'timeout'
    seconds for results to be produced. Any exceptions thrown are forwarded
    to the client.
    """
    return run_worker_tasks(cf.ThreadPoolExecutor, worker_tasks, thread_n, timeout)


def run_threads(worker, tasks, thread_n=4, timeout=300):
    """
    Runs function 'worker' on 'thread_n' number of threads. The 'worker'
    function must take one of the 'tasks' and produce a result that will be
    returned to the client. 'timeout' is the number of seconds to wait for
    results to be produced. Any exceptions thrown are forwarded to the client.
    """
    worker_tasks = [(worker, task) for task in tasks]
    return run_worker_tasks(cf.ThreadPoolExecutor, worker_tasks, thread_n, timeout)


def _worker_proc_(payload):
    logger = get_logger()
    worker, proc_init, proc_args, tasks, thread_n, timeout = payload
    if proc_init is not None:
        proc_obj = proc_init(proc_args)
    else:
        proc_obj = proc_args
    tasks = [(logger, proc_obj, task) for task in tasks]
    results = []
    for x in run_threads(worker, tasks, thread_n, timeout):
        if isinstance(x, Exception):
            raise x
        results.append(x)
    return results


def run_concurrent(worker,
                   tasks,
                   proc_n=4,
                   thread_n=4,
                   proc_init=None,
                   proc_args=None,
                   timeout=60):
    """
    Runs function 'worker' to process list of 'tasks' using 'proc_n' number of
    processes, each of which runs 'thread_n' number of threads. The 'worker'
    excepts three arguments: logger, 'args' passed through,
    and one of the tasks. The 'worker' will either produce a result or raise
    an exception. Exceptions will be forwarded to the client.
    """
    if len(tasks) < proc_n * thread_n:
        raise ValueError("Not enough processes and threads for the tasks.")

    # Split the tasks into chunks for each process.
    payloads = [(worker,
                 proc_init,
                 proc_args,
                 [tasks[i] for i in range(len(tasks)) if i % proc_n == p],
                 thread_n,
                 timeout)
                for p in range(proc_n)]

    # Run the processes.
    for results in run_procs(_worker_proc_, payloads, proc_n, timeout):
        for result in results:
            yield result
