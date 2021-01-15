#!/usr/bin/env python3

# strict_fsh.py - strict file system hierarchy
#
# Copyright (c) 2005-2011 Fpemud <fpemud@sina.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
strict_fsh

@author: Fpemud
@license: GPLv3 License
@contact: fpemud@sina.com
"""

import os
import pwd
import grp
import glob

__author__ = "fpemud@sina.com (Fpemud)"
__version__ = "0.0.1"


class FshCheckError(Exception):
    pass


class FileSystemHierarchy:

    """We comply with FHS (https://refspecs.linuxfoundation.org/fhs.shtml) but have some our own rules:
       1. Fedora UsrMerge (https://fedoraproject.org/wiki/Features/UsrMove)
       2. using /home/root as root's home directory, and symlink /root to it
       3. toolchain directory in /usr
       4. no /usr/local
       5. optional swap file /var/swap.dat
    """

    def __init__(self, dirPrefix="/"):
        self._dirPrefix = dirPrefix
        self._record = set()

    def check(self):
        self._check(False)

    def fixate(self):
        self._check(True)

    def _check(self, bAutoFix):
        self.bAutoFix = bAutoFix

        # /bin
        self._checkSymlink("/bin", "usr/bin")

        # /boot
        self._checkDir("/boot")
        self._checkEntryMetadata("/boot", 0o755, "root", "root")

        # /dev
        self._checkDir("/dev")
        self._checkEntryMetadata("/dev", 0o755, "root", "root")

        # /etc
        self._checkDir("/etc")
        self._checkEntryMetadata("/etc", 0o755, "root", "root")

        # /home
        self._checkDir("/home")
        self._checkEntryMetadata("/home", 0o755, "root", "root")

        # /home/X
        for fn in self._glob("/home/*"):
            self._checkDir(fn)
            self._checkEntryMetadata(fn, 0o700, os.path.basename(fn), os.path.basename(fn))
        if not self._exists("/home/root"):
            # no way to autofix
            raise FshCheckError("\"/home/root\" does not exist")

        # /lib
        self._checkSymlink("/lib", "usr/lib")

        # /lib64
        self._checkSymlink("/lib64", "usr/lib64")

        # /mnt
        self._checkDir("/mnt")
        self._checkEntryMetadata("/mnt", 0o755, "root", "root")

        # /opt
        if self._exists("/opt"):
            # /opt
            self._checkDir("/opt")
            self._checkEntryMetadata("/opt", 0o755, "root", "root")

            # /opt/bin
            if self._exists("/opt/bin"):
                self._checkDir("/opt/bin")
                self._checkEntryMetadata("/opt/bin", 0o755, "root", "root")

        # /proc
        self._checkDir("/proc")
        self._checkEntryMetadata("/proc", 0o755, "root", "root")

        # /root
        self._checkSymlink("/root", "home/root")

        # /run
        self._checkDir("/run")
        self._checkEntryMetadata("/run", 0o755, "root", "root")

        # /sbin
        self._checkSymlink("/sbin", "usr/sbin")

        # /sys
        self._checkDir("/sys")
        self._checkEntryMetadata("/sys", 0o755, "root", "root")

        # /tmp
        self._checkDir("/tmp")
        self._checkEntryMetadata("/tmp", 0o755, "root", "root")        # FIXME

        # /usr
        self._checkDir("/usr")
        self._checkEntryMetadata("/usr", 0o755, "root", "root")

        # /usr/bin
        self._checkDir("/usr/bin")
        self._checkEntryMetadata("/usr/bin", 0o755, "root", "root")

        # /usr/games
        if self._exists("/usr/games"):
            # /usr/games
            self._checkDir("/usr/games")
            self._checkEntryMetadata("/usr/games", 0o755, "root", "root")

            # /usr/games/bin
            if self._exists("/usr/games/bin"):
                self._checkDir("/usr/games/bin")
                self._checkEntryMetadata("/usr/games/bin", 0o755, "root", "root")

        # /usr/include
        self._checkDir("/usr/include")
        self._checkEntryMetadata("/usr/include", 0o755, "root", "root")

        # /usr/lib
        self._checkDir("/usr/lib")
        self._checkEntryMetadata("/usr/lib", 0o755, "root", "root")

        # /usr/lib64
        self._checkDir("/usr/lib64")
        self._checkEntryMetadata("/usr/lib64", 0o755, "root", "root")

        # /usr/libexec
        self._checkDir("/usr/libexec")
        self._checkEntryMetadata("/usr/libexec", 0o755, "root", "root")

        # /usr/sbin
        self._checkDir("/usr/sbin")
        self._checkEntryMetadata("/usr/sbin", 0o755, "root", "root")

        # /usr/share
        self._checkDir("/usr/share")
        self._checkEntryMetadata("/usr/share", 0o755, "root", "root")

        # /usr/src
        if self._exists("/usr/src"):
            self._checkDir("/usr/src")
            self._checkEntryMetadata("/usr/src", 0o755, "root", "root")

        # toolchain directory
        for fn in self._glob("/usr/*-*-*-*"):
            self._checkDir(fn)
            self._checkEntryMetadata(fn, 0o755, "root", "root")

        # /var
        self._checkDir("/var")
        self._checkEntryMetadata("/var", 0o755, "root", "root")

        # /var/cache
        if self._exists("/var/cache"):
            self._checkDir("/var/cache")
            self._checkEntryMetadata("/var/cache", 0o755, "root", "root")

        # /var/db
        if self._exists("/var/db"):
            self._checkDir("/var/db")
            self._checkEntryMetadata("/var/db", 0o755, "root", "root")

        # /var/games
        if self._exists("/var/games"):
            self._checkDir("/var/games")
            self._checkEntryMetadata("/var/games", 0o755, "root", "root")

        # /var/lib
        if self._exists("/var/lib"):
            self._checkDir("/var/lib")
            self._checkEntryMetadata("/var/lib", 0o755, "root", "root")

        # /var/lock
        if self._exists("/var/lock"):
            self._checkSymlink("/var/lock", "/run/lock")

        # /var/log
        if self._exists("/var/log"):
            self._checkDir("/var/log")
            self._checkEntryMetadata("/var/log", 0o755, "root", "root")

        # /var/run
        if self._exists("/var/run"):
            self._checkSymlink("/var/run", "/run")

        # /var/spool
        if self._exists("/var/spool"):
            self._checkDir("/var/spool")
            self._checkEntryMetadata("/var/spool", 0o755, "root", "root")

        # /var/swap.dat
        if self._exists("/var/swap.dat"):
            self._checkFile("/var/swap.dat")
            self._checkEntryMetadata("/var/swap.dat", 0o600, "root", "root")

        # /var/tmp
        self._checkDir("/var/tmp")
        self._checkEntryMetadata("/var/tmp", 0o755, "root", "root")

        # redundant files
        self._checkNoRedundantEntry("/")
        self._checkNoRedundantEntry("/usr")
        self._checkNoRedundantEntry("/var")

    def _exists(self, fn):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        return os.path.exists(fullfn)

    def _glob(self, fn):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        ret = glob.glob(fullfn)
        ret = [x[len(self._dirPrefix):] for x in ret]
        return ret

    def _checkDir(self, fn):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        if not os.path.exists(fullfn):
            if self.bAutoFix:
                os.mkdir(fullfn)
            else:
                raise FshCheckError("\"%s\" does not exist" % (fn))

        if os.path.islink(fullfn) or not os.path.isdir(fullfn):
            # no way to autofix
            raise FshCheckError("\"%s\" is invalid" % (fn))

        self._record.add(fn)

    def _checkFile(self, fn):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        if not os.path.exists(fullfn):
            # no way to autofix
            raise FshCheckError("\"%s\" does not exist" % (fn))

        if os.path.islink(fullfn) or not os.path.isfile(fullfn):
            # no way to autofix
            raise FshCheckError("\"%s\" is invalid" % (fn))

        self._record.add(fn)

    def _checkSymlink(self, fn, target):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        if not os.path.exists(fullfn):
            if self.bAutoFix:
                os.symlink(target, fullfn)
            else:
                raise FshCheckError("\"%s\" does not exist" % (fn))

        if not os.path.islink(fullfn) or not os.readlink(fullfn) != target:
            # FIXME: implement autofix
            raise FshCheckError("\"%s\" is invalid" % (fn))

        self._record.add(fn)

    def _checkEntryMetadata(self, fn, mode, owner, group):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        ownerId = pwd.getpwnam(owner).pw_uid
        groupId = grp.getgrnam(group).gr_gid

        s = os.stat(fullfn)
        if s.st_mode != mode:
            if self.bAutoFix:
                os.chmod(fullfn, mode)
            else:
                raise FshCheckError("\"%s\" has invalid permission" % (fn))
            if s.st_uid != ownerId:
                if self.bAutoFix:
                    os.chown(fullfn, ownerId, s.st_gid)
                else:
                    raise FshCheckError("\"%s\" has invalid owner" % (fn))
            if s.st_gid != groupId:
                if self.bAutoFix:
                    os.chown(fullfn, s.st_uid, groupId)
                else:
                    raise FshCheckError("\"%s\" has invalid owner group" % (fn))

        self._record.add(fn)

    def _checkNoRedundantEntry(self, fn):
        assert os.path.isabs(fn)
        fullfn = os.path.join(self._dirPrefix, fn[1:])

        for fn2 in os.listdir(fullfn):
            fullfn2 = os.path.join(fullfn, fn2)
            if fullfn2 not in self._record:
                raise FshCheckError("\"%s\" should not exist" % (fullfn2[len(self._dirPrefix):]))