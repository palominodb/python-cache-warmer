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
                       [-p PROCESSLIST] [-i START_INTERVAL] [-s STEP]
                       [-e EXECUTE] [-S SOCKET] [-t TARGET_SLOW_QUERY_COUNT]
                       [-T CONSECUTIVE_TARGET_MET_LIMIT] [-v]

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
  -i START_INTERVAL, --start_interval START_INTERVAL
                        starting interval, in seconds (default: 30)
  -s STEP, --step STEP  interval step, in seconds (default: 5)
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
  -v, --verbosity       verbose, can be supplied many times to increase
                        verbosity (default: None)
```

Sample Usage and Output
-----------------------
```
(py26)[sandbox@ip-10-136-86-222 python-cache-warmer]$ ./cache_warmer.py -p h=localhost,u=sandbox,p=sandbox -e h=192.168.2.113,u=sandbox,p=sandbox -i 10 -s 5 -t 2 -T 2 -vv
Starting /usr/bin/pt-query-digest with interval=10
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 10 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.2.113,u=sandbox,p=sandbox
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 162
First check, retrieving another slow query count...
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 164
Slow query count has increased, will now start checking for target slow query count.
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 166
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 1x.
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 168
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 2x.
Consecutive target met limit has been reached.
Starting /usr/bin/pt-query-digest with interval=5
cmd: /usr/bin/pt-query-digest --processlist h=localhost,u=sandbox,p=sandbox --interval 5 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=192.168.2.113,u=sandbox,p=sandbox
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 170
First check, retrieving another slow query count...
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 172
Slow query count has increased, will now start checking for target slow query count.
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 174
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 1x.
cmd: mysqladmin -h 192.168.2.113 -u sandbox -psandbox status
Slow query count: 176
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count was met consecutively 2x.
Consecutive target met limit has been reached.
(py26)[sandbox@ip-10-136-86-222 python-cache-warmer]$
```
