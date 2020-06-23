#!/usr/bin/python3.6

import os
import os.path as osp
import glob
import sys
from subprocess import run, PIPE
import time
import re


SLEEP=3 # seconds
SSH='/bin/ssh'
STAT="top -b -n1 -d1 | head -n4 | tail -n2 | tr '\n' ',' | xargs echo | sed 's/[^0-9,.]//g' | head -c -2"
HEADER='us,sy,ni,id,wa,hi,si,st,tot,free,used,buff\n'
LOG_DIR='/var/log/mon'
GROUPFILEDIR='/root/.mon/groups'

def errmsg(msg):
  sys.stderr.write(msg + '\n')
  sys.stderr.flush()

def collect_usage_stats(grpname, ip, atime):
  os.makedirs(osp.join(LOG_DIR, grpname, ip), exist_ok=True)
  logname = osp.join(LOG_DIR, grpname, ip, str(atime))
  command = [SSH, ip, STAT]
  output = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

  # write any errors
  if len(output.stderr) > 0:
    errmsg('stderr for IP %s in group %s:' % (str(ip), str(grpname)))
    errmsg(output.stderr)
  # Below is for just output 'stat'
  # lines = output.stdout.split('\n')
  # for line in range(len(lines)):
  #   lines[line] = re.sub(r'\s+', ',', lines[line]).strip()
  # if len(lines) > 1:  # Trim out the useless first line output by vmstat
  #   lines = lines[1:]
  line = output.stdout
  with open(logname, 'w') as logfile:
    logfile.write(HEADER + line)

def collect_group(groups, grpname):
  IPs = groups[grpname]
  t = int(round(time.time() * 1000))
  for ip in IPs:
    try:
      collect_usage_stats(grpname, ip, t)
    except Exception as e:
      errmsg('Error collecting stats for IP %s in group %s: %s' % (str(ip), str(grpname), str(e)))

def capture_stats():
  # read the groups in from the groupfile(s)
  groups = {}
  for groupfile in glob.glob(osp.join(GROUPFILEDIR, '*')):
    try:
      groups.update(eval(open(groupfile, 'r').read()))
    except Exception as e:
      errmsg('Error reading groupfile %s: %s' % (groupfile, str(e)))
    

  # monitor each IP in each group
  for group in groups.keys():
    try:
      collect_group(groups, group)
    except Exception as e:
      errmsg('Error collecting stats for group %s: %s' % (str(group), str(e)))
  

if __name__ == '__main__':
  while True:
    capture_stats()
    time.sleep(SLEEP)
