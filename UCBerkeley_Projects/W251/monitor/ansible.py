#!/usr/bin/python3.6

import re
import os
import os.path as osp
import time
from subprocess import run, PIPE

GROUPS_DIR = '/root/.mon/groups'

def get_ansible_inventory_contents():
  ansible_cfg = open('/etc/ansible/ansible.cfg', 'r').read().split('\n')
  ansible_cfg = list(map(lambda x: re.sub('\s+', ' ', x), ansible_cfg))
  inventory = list(filter(lambda x: x.startswith('inventory =') or x.startswith('inventory='), ansible_cfg))[0]
  location = inventory.split('=')[1].strip()
  return location

def parse_inventory(inv):
  inv_conts = open(inv, 'r').read().split('\n')
  host_map = {}
  hosts = {}
  grp_hosts = set()
  grp = None
  for line in inv_conts:
    if len(line.strip()) == 0:
      continue
    cre = re.match(r'\[(.*)\]', line)
    if cre is not None:
      grp = cre.group(1)
      grp_hosts = set()
      continue
    mmre = re.match(r'(.*) ansible_ssh_host=(.*)', line)
    if mmre is not None:
      host_map[mmre.group(1)] = mmre.group(2)
      continue
    host = line.split(' ')[0].strip()
    if grp is not None:
      cmd = ['getent', 'hosts', host]
      if len(run(cmd, stdout=PIPE).stdout) > 0:
        grp_hosts.add(host)
      else:
        grp_hosts.add(host_map[host])
      hosts[grp] = list(grp_hosts)
  return hosts

def write_groups(groups, groups_dir):
  os.makedirs(groups_dir, exist_ok=True)
  for d in os.listdir(groups_dir):
    os.remove(osp.join(groups_dir, d))
    # print('would be removing %s' % osp.join(groups_dir, d))
  for grp in groups.keys():
    with open(osp.join(groups_dir, grp), 'w') as grpfile:
      grpfile.write(str({grp: groups[grp]}))
    

if __name__ == '__main__':
  while True:
    try:
      ansible_inventory = get_ansible_inventory_contents()
      python_inventory = parse_inventory(ansible_inventory)
      write_groups(python_inventory, GROUPS_DIR)
    except Exception as e:
      print(e)
    time.sleep(10)
