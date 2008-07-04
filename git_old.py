#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2007 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Requires: git v1.5.2 or below
# For git v1.5.3 (or higher) use "git.py" instead
#
# this module for git support is supposed to be removed as soon as no major
# distribution contains git before v1.5.3 anymore
#


from translate.storage.versioncontrol import run_command
from translate.storage.versioncontrol import GenericRevisionControlSystem
import re


def is_available():
    """check if git v1.5.2 (or below) is installed"""
    exitcode, output, error = run_command(["git", "--version"])
    if exitcode != 0:
        # no client available
        return False
    # check if the version number is below 1.5.3
    # synchronize any changes below with "is_available" in "git.py"
    if re.search(r'\s0\.', output) or \
            re.search(r'\s1\.[0-4]$', output) or \
            re.search(r'\s1\.[0-4]\.', output) or \
            re.search(r'\s1\.5$', output) or \
            re.search(r'\s1\.5\.[0-2]', output):
        # git seems to be below v1.5.3
        return True
    # git seems to be at v1.5.3 or higher
    return False


class git_old(GenericRevisionControlSystem):
    """Class to manage items under revision control of git."""

    RCS_METADIR = ".git"
    SCAN_PARENTS = True

    def _get_git_dir(self):
        """git requires the git metadata directory for every operation
        """
        import os
        return os.path.join(self.root_dir, self.RCS_METADIR)

    def _get_git_command(self, args):
        """prepends generic git arguments to conrete ones
        """
        command = ["git", "--git-dir", self._get_git_dir(), "--work-tree", self.root_dir]
        command.extend(args)
        return command
    
    def update(self, revision=None):
        """Does a clean update of the given path"""
        # git checkout
        command = self._get_git_command(["checkout", self.location_rel])
        exitcode, output_checkout, error = run_command(command)
        if exitcode != 0:
            raise IOError("[GIT] checkout failed (%s): %s" % (command, error))
        # pull changes
        command = self._get_git_command(["pull"])
        exitcode, output_pull, error = run_command(command)
        if exitcode != 0:
            raise IOError("[GIT] pull failed (%s): %s" % (command, error))
        return output_checkout + output_pull

    def commit(self, message=None):
        """Commits the file and supplies the given commit message if present"""
        # add the file
        command = self._get_git_command(["add", self.location_rel])
        exitcode, output_add, error = run_command(command)
        if exitcode != 0:
            raise IOError("[GIT] add of ('%s', '%s') failed: %s" \
                    % (self.root_dir, self.location_rel, error))
        # commit file
        command = self._get_git_command(["commit"])
        if message:
            command.extend(["-m", message])
        exitcode, output_commit, error = run_command(command)
        if exitcode != 0:
            if len(error):
                msg = error
            else:
                msg = output_commit
            raise IOError("[GIT] commit of ('%s', '%s') failed: %s" \
                    % (self.root_dir, self.location_rel, msg))
        # push changes
        command = self._get_git_command(["push"])
        exitcode, output_push, error = run_command(command)
        if exitcode != 0:
            raise IOError("[GIT] push of ('%s', '%s') failed: %s" \
                    % (self.root_dir, self.location_rel, error))
        return output_add + output_commit + output_push

    def getcleanfile(self, revision=None):
        """Get a clean version of a file from the git repository"""
        # run git-show
        command = self._get_git_command(["show", "HEAD:%s" % self.location_rel])
        exitcode, output, error = run_command(command)
        if exitcode != 0:
            raise IOError("[GIT] 'show' failed for ('%s', %s): %s" \
                    % (self.root_dir, self.location_rel, error))
        return output
