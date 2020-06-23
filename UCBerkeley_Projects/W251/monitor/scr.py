#!/usr/bin/python3.6

import curses
from curses import wrapper
import pandas as pd
import os
import os.path as osp
import time
import sys

LOGS_FILE = '/root/.mon/logs.csv'

def get_util(f):
  util_df = pd.read_csv(f)
  util_df['time'] = pd.to_datetime(util_df['time'])
  return util_df

def floatpos(f):
  return '{:.2f}'.format(f).zfill(5)

def get_stats(df):
  usage_mem = (1 - (df['free'].mean() / df['tot'].mean())) * 100
  usage_cpu = 100 - df['id'].mean()
  last_heartbeat = df['time'].max()
  most_recent = df[df['time'] == last_heartbeat]
  mem_free = most_recent['free'].sum() / 1024
  mem_tot = most_recent['tot'].sum() / 1024
  seconds_since = (pd.to_datetime(time.time() * 1000000000) - last_heartbeat).total_seconds()
  
  return usage_mem, usage_cpu, mem_free, mem_tot, seconds_since


def draw_background(stdscr):
  stdscr.border()
  stdscr.bkgdset(' ', curses.color_pair(0))
  stdscr.addstr(0, 2, 'Utilization')

def render_node(win, util, node):
  node_data = util[util['node'] == node]
  usage_mem, usage_cpu, free, total, since = get_stats(node_data)
  win.addstr('{0: <36}{1}%  {2}%  {3:.1f}/{4:.1f}{5}{6:.2f}\n'.format('   - ' + node,
                                                              floatpos(usage_cpu),
                                                              floatpos(usage_mem),
                                                              free,
                                                              total,
                                                              ' '*(22-len('{0:.1f}/{1:.1f}'.format(free,total))),
                                                              since))

def render_group(stdscr, util, group, y):
  grp = util[util['group'] == group]
  usage_mem, usage_cpu, free, total, since = get_stats(grp)
  nodes = grp['node'].unique()
  stdscr.addstr('{0: <36}{1}%  {2}%  {3:.1f}/{4:.1f}{5}{6:.2f}\n'.format(' - ' + group,
                                                                 floatpos(usage_cpu),
                                                                 floatpos(usage_mem),
                                                                 free,
                                                                 total,
                                                                 ' '*(22-len('{0:.1f}/{1:.1f}'.format(free,total))),
                                                                 since))
  for node in nodes:
    render_node(stdscr, util, node)
  return len(nodes) + 1
  

def draw_win(stdscr, util):
  groups = util['group'].unique()
  stdscr.addstr('\n')
  stdscr.addstr(' '*36 + 'cpu     mem     free/total (MB)       time since last heartbeat (s)\n')
  y = 2
  for group in groups:
    y += render_group(stdscr, util, group, y)
    stdscr.addstr('\n')
  draw_background(stdscr)
  stdscr.addstr(curses.LINES-1, curses.COLS-7, '*w251*')

def main(stdscr):
  stdscr.clear()
  stdscr.erase()
  stdscr.refresh()
  while True:
    stdscr.clear()
    util = get_util(LOGS_FILE)
    draw_win(stdscr, util)
    stdscr.refresh()
    time.sleep(3)

if __name__ == '__main__':
  wrapper(main)
