# -*- python -*-
#
# Tim Hawes <me@timhawes.com>
# 15th November 2006

"""
Atomic file writer.
"""

import grp
import os
import pwd
import tempfile
import filecmp

__all__ = ['AtomicWriter']

class AtomicWriter:
    """Safely writes to a file, avoiding incomplete or corrupted files by
    atomically renaming it after completion.
    """

    def __init__(self, filename, mode=None, tmp_suffix=None, user=None, group=None, detect_conflict=False, compare=False):
        # tmp_suffix is deprecated and ignored
        self.filename = filename
        self.tempfd, self.tempfilename = tempfile.mkstemp(dir=os.path.dirname(filename))
        self.tempfile = os.fdopen(self.tempfd, "w")
        self.detect_conflict = detect_conflict
        self.compare = compare
        if self.detect_conflict:
            try:
                self.initial_stat = os.stat(self.filename)
            except OSError:
                self.initial_stat = None
        if mode:
            os.chmod(self.tempfilename, mode)
            self.auto_chmod = False
        else:
            self.auto_chmod = True
        if user:
            u = pwd.getpwnam(user)
            uid = u.pw_uid
            gid = u.pw_gid
            if group:
                g = grp.getgrnam(group)
                gid = g.gr_gid
            os.chown(self.tempfilename, uid, gid)
            self.auto_chown = False
        else:
            self.auto_chown = True

    def __len__(self):
        return int(self.tempfile.tell())

    def write(self, data):
        self.tempfile.write(data)

    def commit(self):
        self.tempfile.close()
        try:
            st = os.stat(self.filename)
            if self.detect_conflict:
                if self.initial_stat != st:
                    raise IOError("%s changed while we were using it" % (self.filename))
            if self.auto_chmod:
                os.chmod(self.tempfilename, st.st_mode)
            if self.auto_chown:
                os.chown(self.tempfilename, st.st_uid, st.st_gid)
        except OSError:
            pass
        if self.compare:
            if os.path.exists(self.filename) and filecmp.cmp(self.filename, self.tempfilename):
                # new file is identical to the old one
                os.unlink(self.tempfilename)
                return
        os.rename(self.tempfilename, self.filename)

    def rollback(self):
        self.tempfile.close()
        os.unlink(self.tempfilename)

    def __del__(self):
        try:
            self.tempfile.close()
            os.unlink(self.tempfilename)
        except:
            pass
