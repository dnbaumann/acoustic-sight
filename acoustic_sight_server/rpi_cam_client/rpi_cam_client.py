import os
import subprocess
import sys


DIR = os.path.dirname(os.path.realpath(__file__))


def run_client(*args):
    os.environ['PATH'] = '/usr/local/bin:{path}'.format(path=os.environ['PATH'])
    cmd = ['node', os.path.join(DIR, 'app.js')] + list(args)
    subprocess.run(cmd)


if __name__ == '__main__':
    run_client(*sys.argv[1:])
