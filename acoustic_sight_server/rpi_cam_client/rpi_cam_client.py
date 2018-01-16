import multiprocessing
import os
import signal
import subprocess
import sys


DIR = os.path.dirname(os.path.realpath(__file__))
PIDFILE = os.path.join('/tmp/rpi_cam_client.pid')


def get_node_path():
    cmd = ['/usr/bin/env', 'which', 'node']
    return subprocess.check_output(cmd).decode().strip()


def kill_by_pidfile(pidfile=PIDFILE):
    if os.path.isfile(pidfile):
        with open(pidfile) as f:
            pid = int(f.read())

        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        os.remove(pidfile)


def run_client(*args):
    kill_by_pidfile(PIDFILE)

    cmd = [get_node_path(), os.path.join(DIR, 'app.js')] + list(args)
    proc = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

    with open(PIDFILE, 'w') as f:
        f.write('%s' % proc.pid)

    try:
        (output, error) = proc.communicate()

        if error:
            raise ChildProcessError('Failed to run subprocess: {error}'.format(error=error))
        else:
            return output
    except KeyboardInterrupt:
        pass


class RPiCamClientProcess(multiprocessing.Process):
    def terminate(self):
        super().terminate()
        kill_by_pidfile(PIDFILE)


if __name__ == '__main__':
    run_client(*sys.argv[1:])
