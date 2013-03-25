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
                       [-e EXECUTE] [-t TARGET_SLOW_QUERY_COUNT] [-v]

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
  -t TARGET_SLOW_QUERY_COUNT, --target-slow-query-count TARGET_SLOW_QUERY_COUNT
                        Target slow query count to look for before terminating
                        pt-query-digest script. (default: 2)
  -v, --verbosity       verbose, can be supplied many times to increase
                        verbosity (default: None)
```

Sample Usage and Output
-----------------------
```
(py26)[sandbox@ip-10-136-86-222 python-cache-warmer]$ ./cache_warmer.py -p h=10.136.86.222,u=sandbox,p=sandbox -i 30 -s 5 -e h=10.142.214.140,u=sandbox,p=sandbox -t 2
Starting /usr/bin/pt-query-digest with interval=30
Found 3 new slow query(ies) on 'execute' instance.
Found 5 new slow query(ies) on 'execute' instance.
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
Starting /usr/bin/pt-query-digest with interval=25
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
Starting /usr/bin/pt-query-digest with interval=20
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
Starting /usr/bin/pt-query-digest with interval=15
Found 6 new slow query(ies) on 'execute' instance.
Found 4 new slow query(ies) on 'execute' instance.
Found 4 new slow query(ies) on 'execute' instance.
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
Starting /usr/bin/pt-query-digest with interval=10
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
Starting /usr/bin/pt-query-digest with interval=5
Found 6 new slow query(ies) on 'execute' instance.
Found 4 new slow query(ies) on 'execute' instance.
Found 4 new slow query(ies) on 'execute' instance.
Found 2 new slow query(ies) on 'execute' instance.
Target slow query count met.
(py26)[sandbox@ip-10-136-86-222 python-cache-warmer]$
```