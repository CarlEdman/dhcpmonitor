#!/usr/bin/env python3
#
# Monitor dhcp lease file for given devices dropping out
#
# usage: dhcp_monitor.py [-h] [--version] [--file LEASEFILE] hostid+
#
# positional arguments:
#   hostid      Local hostname, IP address, or MAC address to monitor
#
# optional arguments:
#   -h, --help                  show this help message and exit
#   --version                   show program's version number and exit
#   -l, --leasefile LEASEFILE   Location of dhcp lease file; defaults to '/var/dhcp.leases'
#
# Note that command line arguments may be specified in a FILE, one to a line, by instead giving
# the argument "@FILE".
#

prog='dhcp_monitor'
version='0.1'
author='Carl Edman (CarlEdman@gmail.com)'

import os
import sys
import time
import argparse

parser = argparse.ArgumentParser(description='Monitor dhcp lease file for given devices dropping out', fromfile_prefix_chars='@')

parser.add_argument('--version', action='version',
  version='{} {}'.format(prog, version))

parser.add_argument('hostid', type=str, nargs='+',
  help='local hostname or MAC address to monitor')

parser.add_argument('-l', '--leasefile', type=bytes, default=b'/var/dhcp.leases',
  help='Location of dhcp lease file')

parser.add_argument('-s', '--sleeptime', type=int, default=60,
  help='How long to sleep, in seconds, between polls of the lease file.')

args = parser.parse_args()

def check(online):
  with open(args.leasefile) as lf: ls = [l.strip().split(' ') for l in lf]
  current = {}
  for l in ls:
    current[l[1]] = l
    current[l[2]] = l
    current[l[3]] = l

  going_on  = []
  going_off = []

  for hid in online:
    if online[hid] == (hid in current):
      continue
    online[hid] = hid in current
    if online[hid]:
      going_on.append(hid)
    else:
      going_off.append(hid)

  return (going_on, going_off)

def main():
  online = { a:True for a in args.hostid }
  otime = 0

  while True:
    ntime = os.stat(args.leasefile).st_mtime
    if ntime == otime:
      time.sleep(args.sleeptime)
    else:
      otime = ntime
      going_on, going_off = check(online)

      if going_off:
        print('{}: {} went offline.'.format(time.ctime(ntime), ",".join(going_off)))

      if going_on:
        print('{}: {} came online.'.format(time.ctime(ntime), ",".join(going_on)))

if __name__ == '__main__':
  main()
