#!/usr/bin/env python3

import sys
import os
import subprocess

OBJECTS_PATH = './.git/objects'
CWD = os.getcwd()

def show_banner():
    print("""\
      ___      ___
       O        O
    ________________
    |__|__|__|__|__|
    |              |
    |______________|
    |__|__|__|__|__|


Usage: ./dump-git_obj.py <dir>

> which dir that is absolute and contains .git dir\
    """)

def dump_file(cdir):
    if not os.path.exists(f'{CWD}/results'):
        os.makedirs(result_path)

    for fname in os.listdir(f'{OBJECTS_PATH}/{cdir}'):
        result = subprocess.check_output(f'git cat-file -p {cdir}{fname}', shell=True)
        result_path = f'{CWD}/results/{cdir}'

        if not os.path.exists(result_path):
            os.mkdir(result_path)

        with open(f'{result_path}/{fname}', 'w') as f:
            f.write(result.decode(encoding='utf-8', errors='ignore'))

if len(sys.argv) != 2:
    show_banner()
    exit(1)

try:
    os.chdir(sys.argv[1])
except:
    print("invalid path")
    show_banner()
    exit(1)

rootdir = os.listdir(OBJECTS_PATH)
rootdir.sort()

for subdir in rootdir:
    if len(subdir) == 2:
        dump_file(subdir)
