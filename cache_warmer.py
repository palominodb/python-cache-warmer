#!/usr/bin/env python
"""Python Cache Warmer"""
from pprint import pprint as pp
import threading
import re
import shlex
import subprocess
import sys
import traceback
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time
import yaml


OPTS = None


class OptionsBuilder(object):
    """Class for merging options from command-line arguments and config file."""

    @classmethod
    def get_options(cls):
        """Returns merged options from command-line arguments and config file."""

        args = cls._parse_args()
        opts = cls._build_opts(args)
        if args.config:
            config_opts = cls._build_config_opts(args.config)
            opts.update(config_opts)

        class Namespace(object):
            pass

        ns = Namespace()
        for k, v in opts.iteritems():
            setattr(ns, k, v)
        return ns

    @classmethod
    def _parse_args(cls):
        """Parses command line arguments."""

        parser = ArgumentParser(
            description='Cache warmer.',
            formatter_class=ArgumentDefaultsHelpFormatter)

        parser.add_argument('-C', '--config',
            help='config file to load options from')

        parser.add_argument('-x', '--pt-query-digest-path',
            default='/usr/bin/pt-query-digest',
            help='pt-query-digest path.')

        parser.add_argument('-p', '--processlist',
            help="processlist DSN. Poll this DSN's processlist for queries, with --interval sleep between.")

        parser.add_argument('-i', '--start_interval',
            type=int, default=30, help='starting interval, in seconds')

        parser.add_argument('-s', '--step',
            type=int, default=5, help='interval step, in seconds')

        parser.add_argument('-e', '--execute',
            help='execute DSN. Execute queries on this DSN')

        parser.add_argument('-t', '--target-slow-query-count',
            default=2, type=int,
            help='Target slow query count to look for before terminating pt-query-digest script.')

        parser.add_argument('-v', '--verbosity',
            action='count',
            help="verbose, can be supplied many times to increase verbosity")

        args = parser.parse_args()

        return args

    @classmethod
    def _build_opts(cls, args):
        """Builds options from parsed arguments."""

        opts = {}

        opts['config'] = args.config
        opts['pt_query_digest_path'] = args.pt_query_digest_path
        opts['processlist'] = args.processlist
        opts['start_interval'] = args.start_interval
        opts['step'] = args.step
        opts['execute'] = args.execute
        opts['target_slow_query_count'] = args.target_slow_query_count
        opts['verbosity'] = args.verbosity

        return opts

    @classmethod
    def _build_config_opts(cls, filename):
        """Builds options from config file."""

        try:
            with open(filename) as f:
                opts = yaml.load(''.join(f.readlines()))
            return opts
        except IOError, e:
            print 'ERROR %s: %s' % (type(e), e)
            sys.exit()


def run_pt_query_digest(interval):
    v = OPTS.verbosity
    #pt-query-digest --processlist h=10.136.79.115,u=sandbox,p=sandbox --interval 5 --filter '$event->{arg} =~ m/^SELECT/i' --execute h=10.143.15.238,u=sandbox,p=sandbox
    cmd = "%s --processlist %s --interval %s --filter '$event->{arg} =~ m/^SELECT/i' --execute %s"
    cmd = cmd % (OPTS.pt_query_digest_path, OPTS.processlist, interval, OPTS.execute)
    if v >= 2:
        print 'cmd:', cmd
    args = shlex.split(cmd)
    p = None
    try:
        if v >= 4:
            print 'args:', args
        fnull = open(shlex.os.devnull, 'w')
        p = subprocess.Popen(args, stdout=fnull, stderr=fnull)
        if v >= 1:
            '%s started.' % (OPTS.pt_query_digest_path,)
    except Exception, e:
        print 'Failed to run %s.: %s' % (OPTS.pt_query_digest_path, e)
        if v >= 3:
            traceback.print_exc()
    return p


def parse_dsn(dsn):
    v = OPTS.verbosity
    parsed = dict(
        [(i[0].strip(), i[2].strip())
            for i in [word.partition('=')
                for word in dsn.split(',')]])
    if v >= 4:
        print 'dsn:', dsn
        print 'parsed:', parsed
    return parsed


def get_slow_query_count_on_execute_instance():
    v = OPTS.verbosity
    cnt = None
    cmd = 'mysqladmin'
    pdsn = parse_dsn(OPTS.execute)
    if 'h' in pdsn:
        cmd += ' -h %s' % (pdsn['h'],)
    if 'P' in pdsn:
        cmd += ' -P %s' % (pdsn['P'],)
    if 'u' in pdsn:
        cmd += ' -u %s' % (pdsn['u'],)
    if 'p' in pdsn:
        cmd += ' -p%s' % (pdsn['p'],)
    cmd += ' status'
    if v >= 2:
        print 'cmd:', cmd
    args = shlex.split(cmd)
    output = ''
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        while True:
            ln = p.stdout.readline()
            output = output + ln
            if ln == '' and p.poll() is not None:
                break
        output = ' '.join(output.split('\n')).strip()
    except Exception, e:
        print 'Error found while checking mysql status: %s' % (e,)
        if v >= 3:
            traceback.print_exc()

    if v >= 4:
        print 'process output:', output

    pat = re.compile('^.*?Slow queries:\s(?P<count>\d+)', re.IGNORECASE)
    m = pat.match(output)
    if m:
        cnt = int(m.group('count'))
    else:
        if v >= 1:
            print 'No info about slow queries was returned.'

    return cnt


def start_main():
    """Main program logic."""

    global OPTS
    OPTS = OptionsBuilder.get_options()
    v = OPTS.verbosity

    if v >= 4:
        print 'OPTS:'
        pp(OPTS.__dict__)

    last_cnt = None
    interval = OPTS.start_interval
    try:
        while interval > 0:
            print 'Starting %s with interval=%s' % (
                OPTS.pt_query_digest_path, interval)
            pqdp = run_pt_query_digest(interval)
            if pqdp:
                while True:
                    try:
                        cnt = get_slow_query_count_on_execute_instance()
                        if cnt is not None:
                            if v >= 1:
                                print 'Slow query count: %s' % (cnt,)
                            if last_cnt is None:
                                # Store count and get another count for comparison
                                if v >= 1:
                                    print 'First check, retrieving another slow query count...'
                                last_cnt = cnt
                            else:
                                new_slow_queries = cnt - last_cnt
                                last_cnt = cnt
                                if new_slow_queries:
                                    print "Found %s new slow query(ies) on 'execute' instance." % (
                                        new_slow_queries,)
                                if new_slow_queries <= OPTS.target_slow_query_count:
                                    # exit loop and re-run pqd
                                    print 'Target slow query count met.'

                                    # reset last count
                                    last_cnt = None
                                    break
                        time.sleep(0)
                    except KeyboardInterrupt:
                        # Stop checking status and proceed with another instance of pqd
                        break
                pqdp.terminate()
                time.sleep(0)
            else:
                print 'Failed to open process.'
            interval -= OPTS.step
    except KeyboardInterrupt:
        # Exit program
        pass
    except Exception, e:
        print 'An error has occurred: %s' % (e,)
        if v >= 3:
            traceback.print_exc()

if __name__ == "__main__":
    start_main()