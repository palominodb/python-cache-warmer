#!/usr/bin/env python
# ============================================================================
# License: GPL License (see COPYING)
# Copyright 2013 PalominoDB Inc.
# Authors:
# Elmer Medez
# ============================================================================
"""Python Cache Warmer"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pprint import pprint
import shlex
import subprocess
import traceback
import time
import sys
import MySQLdb


def parse_dsn(dsn):
    """Turns DSN string into dict.

    Args:

        dsn: connection option string in pt-query-digest DSN format

    Returns:

        If dsn is equal to "h=localhost,u=sandbox,p=sandbox",
        return value should be:
            {'h': 'localhost', 'u': 'sandbox', 'p': 'sandbox'}
    """

    fld_value_map = dict(
        [(i[0].strip(), i[2].strip())   # i is equal to [field, '=', value]
            for i in [word.partition('=')
                for word in dsn.split(',')]])
    return fld_value_map


class SlowQueryCountChecker(object):
    """Contains count checking logic."""

    def __init__(self, args):
        """Initializes object.

        Args:
            args: The parsed command line arguments.
        """

        super(SlowQueryCountChecker, self).__init__()

        self._args = args
        self._start_checking_for_target = False
        self._last_count = None

        self.consecutive_target_met_count = 0


    def check(self, count):
        """Actual count check logic.

        Args:

            count: new slow query count to check.
        """

        v = self._args.verbosity

        if v >= 1:
            print 'Slow query count: %s' % (count,)

        if self._last_count is None:
            # Store count and get another count for comparison
            self._last_count = count
            if v >= 1:
                print 'First check, waiting for another slow query count...'

        elif self._start_checking_for_target:
            new_slow_queries = count - self._last_count
            self._last_count = count
            print "Found %s new slow query(ies) on 'execute' instance." % (
                new_slow_queries,)

            if new_slow_queries <= self._args.target_slow_query_count:
                self.consecutive_target_met_count += 1
                print 'Target slow query count was met consecutively %sx.' % (
                    self.consecutive_target_met_count,)

            elif self.consecutive_target_met_count > 0:
                # reset consecutive_target_met_count
                self.consecutive_target_met_count = 0
                print 'Counsecutive target met count was reset to %s.' % (
                    self.consecutive_target_met_count,)

            # Reset count if consecutive target met limit was reached
            if (self.consecutive_target_met_count >=
                    self._args.consecutive_target_met_limit):
                print 'Consecutive target met limit was reached.'
                self._last_count = None

        elif not self._start_checking_for_target and count > self._last_count:
            self._start_checking_for_target = True
            self._last_count = count
            if v >= 1:
                print ('Slow query count has increased, will now start '
                       'checking for target slow query count.')

        elif v >= 1:
            print ('Slow query count has not changed, waiting for it to '
                   'increase first before starting to check for target slow '
                   'query count.')


class App(object):
    """Contains main application logic."""

    def __init__(self):
        """Initializes object."""
        super(App, self).__init__()

        self.null = open(shlex.os.devnull, 'w')
        self.args = None

    def _parse_args(self):
        """Parses command line arguments."""

        parser = ArgumentParser(
            description='Cache warmer.',
            formatter_class=ArgumentDefaultsHelpFormatter,
            fromfile_prefix_chars='@')

        parser.add_argument('-x', '--pt-query-digest-path',
            default='/usr/bin/pt-query-digest',
            help='pt-query-digest path.')

        parser.add_argument(
            '-i', '--interval', type=float, default=0.1,
            help='The value of interval, in seconds, to be passed to '
                 'pt-query-digest.')

        parser.add_argument('-p', '--processlist',
            help="processlist DSN. Poll this DSN's processlist for queries, "
                 "with --interval sleep between.")

        parser.add_argument('-e', '--execute',
            help='execute DSN. Execute queries on this DSN')

        parser.add_argument('-S', '--socket',
            help='Socket file to use for connection')

        parser.add_argument('-t', '--target-slow-query-count',
            default=2, type=int,
            help='Target slow query count to look for before terminating '
                 'pt-query-digest script.')

        parser.add_argument('-T', '--consecutive-target-met-limit',
            default=3, type=int,
            help='The number of times target slow query count was met '
                 'consecutively to look for before actually terminating '
                 'pt-query-digest script.')

        parser.add_argument('-m', '--max-execution-time',
            default=600.0, type=float,
            help='Maximum execution time in seconds.')

        parser.add_argument('-d', '--termination-delay',
            default=5, type=int,
            help='Number of seconds to wait before terminating pt-query-digest.')

        parser.add_argument('-v', '--verbosity',
            action='count',
            help='verbose, can be supplied many times to increase verbosity')

        self.args = parser.parse_args()


    def _run_pt_query_digest(self):
        """Runs pt-query-digest executable."""

        v = self.args.verbosity
        cmd = ("%s --processlist %s --interval %s --filter "
               "'$event->{fingerprint} =~ m/^SELECT/i' --execute %s" % (
                   self.args.pt_query_digest_path, self.args.processlist,
                   self.args.interval, self.args.execute))

        if self.args.socket:
            cmd += ' --socket %s' % (self.args.socket,)

        if v >= 2:
            print 'cmd:', cmd

        print 'Starting %s' % (self.args.pt_query_digest_path,)
        p = subprocess.Popen(shlex.split(cmd), stdout=self.null, stderr=self.null)
        if v >= 1:
            '%s started.' % (self.args.pt_query_digest_path,)
        if p:
            time.sleep(self.args.termination_delay)
            p.terminate()
            p.wait()
            print 'pt-query-digest terminated.'


    def _get_slow_query_count_on_execute_instance(self):
        """Returns slow query count on execute instance."""

        pdsn = parse_dsn(self.args.execute)
        connection_options = {}
        if 'h' in pdsn:
            connection_options['host'] = pdsn['h']
        if 'P' in pdsn:
            connection_options['port'] = pdsn['P']
        if 'u' in pdsn:
            connection_options['user'] = pdsn['u']
        if 'p' in pdsn:
            connection_options['passwd'] = pdsn['p']
        if 'S' in pdsn:
            connection_options['unix_socket'] = pdsn['S']

        conn = MySQLdb.connect(**connection_options)
        with conn as cursor:
            sql = "show global status where Variable_name='Slow_queries'"
            cursor.execute(sql)
            row = cursor.fetchone()
            return int(row[1])


    def main(self):
        """Main program logic."""

        self._parse_args()
        v = self.args.verbosity
        if v >= 4:
            print 'args:'
            pprint(self.args)

        try:
            start_time = time.time()
            count_checker = SlowQueryCountChecker(self.args)
            while True:
                self._run_pt_query_digest()
                count = self._get_slow_query_count_on_execute_instance()
                count_checker.check(count)
                if (count_checker.consecutive_target_met_count >=
                        self.args.consecutive_target_met_limit):
                    break
                if time.time() - start_time >= self.args.max_execution_time:
                    print 'Maximum execution time was reached.'
                    break

        except BaseException, e:
            # for all exceptions, exit program with error message.
            if v >= 3:
                traceback.print_exc()
            sys.exit('ERROR %s: %s' % (type(e), e))


if __name__ == '__main__':
    App().main()