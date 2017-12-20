#!/usr/bin/env python3
#
# Monitor dhcp lease file for given devices dropping out
#
# usage: dhcp_monitor.py [-h] [--version] [--file LEASEFILE]
#                        [hostname|macaddress]*
#
# positional arguments:
#   hostname         Local hostname to monitor
#   macaddress       MAC address of interfaces to monitor
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

import sys, argparse

parser = argparse.ArgumentParser(description='Monitor dhcp lease file for given devices dropping out', fromfile_prefix_chars='@')

parser.add_argument('--version', action='version',
  version='{} {}'.format(prog, version))

parser.add_argument('hostname', type=str,
  help='DNS fully-qualified host name')

parser.add_argument('-l', '--leasefile', type=str, default='/var/dhcp.leases',
  help='Location of dhcp lease file')

args = parser.parse_args()

def main():
  pass
  
if __name__ == '__main__':
  main()
