import os
import subprocess
import sys


DIR = os.path.dirname(os.path.realpath(__file__))


def run_client(*args):
    cmd = ['/usr/bin/env', 'node', os.path.join(DIR, 'app.js')] + list(args)
    return subprocess.run(cmd, check=True)


if __name__ == '__main__':
    run_client(*sys.argv[1:])
