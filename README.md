Cache Warmer Script
===================

*Purpose: cache warming.*

Install Requirements
--------------------
`pip install -r requirements.txt`

Usage
-----
```
usage: cache_warmer.py [-h] [-x PT_QUERY_DIGEST_PATH] [-i INTERVAL]
                       [-p PROCESSLIST] [-e EXECUTE] [-S SOCKET]
                       [-t TARGET_SLOW_QUERY_COUNT]
                       [-T CONSECUTIVE_TARGET_MET_LIMIT]
                       [-m MAX_EXECUTION_TIME] [-d TERMINATION_DELAY] [-v]

Cache warmer.

optional arguments:
  -h, --help            show this help message and exit
  -x PT_QUERY_DIGEST_PATH, --pt-query-digest-path PT_QUERY_DIGEST_PATH
                        pt-query-digest path. (default: /usr/bin/pt-query-
                        digest)
  -i INTERVAL, --interval INTERVAL
                        The value of interval, in seconds, to be passed to pt-
                        query-digest. (default: 0.1)
  -p PROCESSLIST, --processlist PROCESSLIST
                        processlist DSN. Poll this DSN's processlist for
                        queries, with --interval sleep between. (default:
                        None)
  -e EXECUTE, --execute EXECUTE
                        execute DSN. Execute queries on this DSN (default:
                        None)
  -S SOCKET, --socket SOCKET
                        Socket file to use for connection (default: None)
  -t TARGET_SLOW_QUERY_COUNT, --target-slow-query-count TARGET_SLOW_QUERY_COUNT
                        Target slow query count to look for before terminating
                        pt-query-digest script. (default: 2)
  -T CONSECUTIVE_TARGET_MET_LIMIT, --consecutive-target-met-limit CONSECUTIVE_TARGET_MET_LIMIT
                        The number of times target slow query count was met
                        consecutively to look for before actually terminating
                        pt-query-digest script. (default: 3)
  -m MAX_EXECUTION_TIME, --max-execution-time MAX_EXECUTION_TIME
                        Maximum execution time in seconds. (default: 600.0)
  -d TERMINATION_DELAY, --termination-delay TERMINATION_DELAY
                        Number of seconds to wait before terminating pt-query-
                        digest. (default: 5)
  -v, --verbosity       verbose, can be supplied many times to increase
                        verbosity (default: None)
```

Sample Usage and Output
-----------------------

```
$ ./cache_warmer.py -p h=localhost,u=sandbox,p=sandbox -e h=192.168.2.110,u=sandbox,p=sandbox -t 4 -T 2 -m 60 -d 5 -vv
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 0.1 --filter '$event->{fingerprint} =~ m/^SELECT/i' --execute h=192.168.2.110,u=sandbox,p=sandbox
Starting /usr/bin/pt-query-digest
pt-query-digest terminated.
Slow query count: 77
First check, waiting for another slow query count...
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 0.1 --filter '$event->{fingerprint} =~ m/^SELECT/i' --execute h=192.168.2.110,u=sandbox,p=sandbox
Starting /usr/bin/pt-query-digest
pt-query-digest terminated.
Slow query count: 81
Slow query count has increased, will now start checking for target slow query count.
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 0.1 --filter '$event->{fingerprint} =~ m/^SELECT/i' --execute h=192.168.2.110,u=sandbox,p=sandbox
Starting /usr/bin/pt-query-digest
pt-query-digest terminated.
Slow query count: 85
Found 4 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 1x.
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 0.1 --filter '$event->{fingerprint} =~ m/^SELECT/i' --execute h=192.168.2.110,u=sandbox,p=sandbox
Starting /usr/bin/pt-query-digest
pt-query-digest terminated.
Slow query count: 89
Found 4 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 2x.
Consecutive target met limit has been reached.
$
```
Using a file to store arguments (use @ to prefix file), the above command is equivalent to:
```
$ ./cache_warmer.py @./args.txt
```

Contents of args.txt:
```
-p
h=localhost,u=sandbox,p=sandbox
-e
h=192.168.2.110,u=sandbox,p=sandbox
-t
4
-T
2
-m
60
-d
5
-vvvv
```