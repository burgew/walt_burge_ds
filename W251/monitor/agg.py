#!/usr/bin/python3.6

import pandas as pd
import os
import os.path as osp
import time

LOGDIR = '/var/log/mon'
OUTDIR = '/root/.mon/logs.csv'
SLEEP = 5  # seconds
KEEP_MINS = 30  # Prune entries older than X mins

TD = pd.Timedelta(KEEP_MINS * 60, unit='s')

def aggregate_node(node_dir):
  node_name = osp.split(node_dir)[1]
  node_files = os.listdir(node_dir)
  df = pd.DataFrame()
  if 'e.csv' in node_files:
    df = pd.read_csv(osp.join(node_dir, 'e.csv'))
    df['time'] = pd.to_datetime(df['time'])
    node_files.remove('e.csv')
  for f in node_files:
    try:
      df = df.append(pd.read_csv(osp.join(node_dir, f)).assign(time=lambda df: pd.to_datetime(int(f) * 1000000)))
    except:
      pass
  df = df[(pd.to_datetime(time.time() * 1000000000) - df['time']) <= TD]
  df.to_csv(osp.join(node_dir, 'e.csv'), index=False)
  for f in node_files:
    try:
      os.remove(osp.join(node_dir, f))
    except:
      pass
  
  return df.assign(node=lambda df: node_name)
  
def aggregate_group(group_dir):
  nodedirs = list(map(lambda x: osp.join(group_dir, x), os.listdir(group_dir)))
  df = pd.concat([aggregate_node(node_dir) for node_dir in nodedirs])
  group_name = osp.split(group_dir)[1]
  return df.assign(group=lambda df: group_name)

def aggregate(log_dir):
  groupdirs = list(map(lambda x: osp.join(log_dir, x), os.listdir(log_dir)))
  df = pd.concat([aggregate_group(group_dir) for group_dir in groupdirs])
  df.to_csv(OUTDIR, index=False)
  # print(df)

if __name__ == '__main__':
  while True:
    aggregate(LOGDIR)
    time.sleep(SLEEP)
