import threading
import sys
import traceback
import os
import signal


def sendKillSignal(etype, value, tb):
    print('KILL ALL')
    traceback.print_exception(etype, value, tb)
    os.kill(os.getpid(), signal.SIGKILL)


original_init = threading.Thread.__init__


def patched_init(self, *args, **kwargs):
    print("Thread initiated")
    original_init(self, *args, **kwargs)
    original_run = self.run

    def patched_run(*args, **kw):
        try:
            original_run(*args, **kw)
        except:
            sys.excepthook(*sys.exc_info())
    self.run = patched_run


def install():
    sys.excepthook = sendKillSignal
    threading.Thread.__init__ = patched_init