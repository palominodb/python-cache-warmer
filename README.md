Cache Warmer Script
===================

*Purpose: cache warming.*

Install Requirements
--------------------
`pip install -r requirements.txt`

Usage
-----
```
usage: cache_warmer.py [-h] [-C CONFIG] [-x PT_QUERY_DIGEST_PATH]
                       [-p PROCESSLIST] [-e EXECUTE] [-S SOCKET]
                       [-t TARGET_SLOW_QUERY_COUNT]
                       [-T CONSECUTIVE_TARGET_MET_LIMIT]
                       [-m MAX_EXECUTION_TIME] [-d TERMINATION_DELAY] [-v]

Cache warmer.

optional arguments:
  -h, --help            show this help message and exit
  -C CONFIG, --config CONFIG
                        config file to load options from (default: None)
  -x PT_QUERY_DIGEST_PATH, --pt-query-digest-path PT_QUERY_DIGEST_PATH
                        pt-query-digest path. (default: /usr/bin/pt-query-
                        digest)
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
(py26)elmer@ElmerSM840:~/palominodb/src/python-cache-warmer$ ./cache_warmer.py -p h=localhost,u=sandbox,p=sandbox -e h=192.168.43.4,u=sandbox,p=sandbox -t 2 -T 2 -m 60 -d 5 -vv
Starting /usr/bin/pt-query-digest
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 1 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.43.4,u=sandbox,p=sandbox
pt-query-digest terminated.
cmd: mysqladmin -h 192.168.43.4 -u sandbox -psandbox status
Slow query count: 28
First check, waiting for another slow query count...
Starting /usr/bin/pt-query-digest
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 1 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.43.4,u=sandbox,p=sandbox
pt-query-digest terminated.
cmd: mysqladmin -h 192.168.43.4 -u sandbox -psandbox status
Slow query count: 30
Slow query count has increased, will now start checking for target slow query count.
Starting /usr/bin/pt-query-digest
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 1 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.43.4,u=sandbox,p=sandbox
pt-query-digest terminated.
cmd: mysqladmin -h 192.168.43.4 -u sandbox -psandbox status
Slow query count: 32
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 1x.
Starting /usr/bin/pt-query-digest
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 1 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.43.4,u=sandbox,p=sandbox
pt-query-digest terminated.
cmd: mysqladmin -h 192.168.43.4 -u sandbox -psandbox status
Slow query count: 34
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 2x.
Consecutive target met limit has been reached.
(py26)elmer@ElmerSM840:~/palominodb/src/python-cache-warmer$

```
