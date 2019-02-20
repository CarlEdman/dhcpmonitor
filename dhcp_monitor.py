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
version='0.2'
author='Carl Edman (CarlEdman@gmail.com)'

import os
import sys
import time
import argparse
import smtplib
import signal
from email.message import EmailMessage

parser = argparse.ArgumentParser(description='Monitor dhcp lease file for given devices dropping out', fromfile_prefix_chars='@')

parser.add_argument('--version', action='version',
  version='{} {}'.format(prog, version))

parser.add_argument('hostid', type=str, nargs='+',
  help='local hostname or MAC address to monitor')

parser.add_argument('-l', '--leasefile', type=str, default='/var/dhcp.leases',
  help='Location of dhcp lease file')

parser.add_argument('-s', '--sleeptime', type=int, default=60,
  help='How long to sleep, in seconds, between polls of the lease file.')

parser.add_argument('--smtp-server', type=str, default='localhost',
  help='SMTP server to use to send emails, optionally followed by a port number.')

parser.add_argument('--smtp-from', type=str, default='DHCP Monitor',
  help='SMTP account from which to send status emails.')

parser.add_argument('--smtp-password', type=str, default=None,
  help='SMTP password, if any, to login in to server.')

parser.add_argument('--smtp-to', type=str, default=None,
  help='E-mail address to send reports to (if not given, reports are sent to standard output).')

parser.add_argument('--daemon', action='store_true',
  help='Run in daemon mode (i.e., detach from console and restart with SIGHUP)')

args = parser.parse_args()

def report(l):
  if args.smtp_to:
    msg = EmailMessage()
    msg['Subject'] = l[0]
    msg['From'] = args.smtp_from
    msg['To'] = args.smtp_to
    msg.set_content('\n'.join(l[1:]))

    (host, port) = args.smtp_server.split(':',1)
    if port: port=int(port)

    with smtplib.SMTP(host=host, port=port) as s:
      s.starttls()
      if args.smtp_from and args.smtp_password:
        s.login(args.smtp_from, args.smtp_password)
      s.send_message(msg)
      s.quit()
  else:
    print('\n'.join(l))

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

def daemonize():
  def closetty(f):
    if f and not f.closed and f.isatty():
      f.close()

#  closetty(sys.stdin)
#  closetty(sys.stdout)
#  closetty(sys.stderr)
 
  def restart(signum, frame):
    os.execv(sys.argv[0],sys.argv)

  signal.signal(signal.SIGHUP, restart)
  

def main():
  if args.daemon: daemonize()

  online = { a:True for a in args.hostid if not a.startswith("#") }
  otime = 0

  while True:
    ntime = os.stat(args.leasefile).st_mtime
    if ntime == otime:
      time.sleep(args.sleeptime)
    else:
      otime = ntime
      going_on, going_off = check(online)

      if going_off:
        report(['{} went offline at {}'.format(",".join(going_off),time.ctime(ntime))])

      if going_on:
        report(['{} came online at {}'.format(",".join(going_on),time.ctime(ntime))])

if __name__ == '__main__':
  main()
