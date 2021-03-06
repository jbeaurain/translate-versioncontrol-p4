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


from translate.storage.versioncontrol import run_command
from translate.storage.versioncontrol import GenericRevisionControlSystem


def is_available():
    """check if p4 is installed and a connection to the server is available"""
    exitcode, output, error = run_command("p4")
    return exitcode == 0


def get_version():
    """return a tuple of (major, minor) for the installed subversion client"""
    exitcode, output, error = run_command(["p4", "-V"])
    
    if exitcode == 0:
        major, minor = output.strip().split("/")[2].split(".")[:2]
        if (major.isdigit() and minor.isdigit()):
            return (int(major), int(minor))
    # something went wrong above
    return (0, 0)


class p4(GenericRevisionControlSystem):
    """Class to manage items under revision control of Subversion."""

    RCS_METADIR = "translate.p4"
    SCAN_PARENTS = True

    def update(self, revision=None):
        """update the working copy - remove local modifications if necessary"""
        # revert the local copy (remove local changes)
        command = ["p4", "revert", self.location_abs]
        exitcode, output_revert, error = run_command(command)
        # any errors?
        if exitcode != 0:
            raise IOError("[P4] Perforce error running '%s': %s" \
                    % (command, error))
        # update the working copy to the given revision
        command = ["p4", "sync"]
        if not revision is None:
            command.append(self.location_abs + "@" + revision)
        if not revision is None:
            command.append(self.location_abs)
        exitcode, output_update, error = run_command(command)
        if exitcode != 0:
            raise IOError("[P4] Perforce error running '%s': %s" \
                    % (command, error))
        return output_revert + output_update

    def commit(self, message=None, author=None):
        """commit the file and return the given message if present

        the 'author' parameter is used for revision property 'translate:author'
        """
        command = ["p4", "submit"]
        
        description = "Submission via translation portal"
  
        if message:
            description = "%s : %s" (description, message)
        command.extend(["-d", description])
        if author:
            description = "%d --- by " % (description, author)
        # the location is the last argument
        command.append(self.location_abs)
        exitcode, output, error = run_command(command)
        if exitcode != 0:
            raise IOError("[P4] Perforce error running '%s': %s" \
                    % (command, error))
        return output
    
    def getcleanfile(self, revision=None):
        """return the content of the 'head' revision of the file"""
        command = ["p4", "cat"]
        if not revision is None:
            command.extend(["-r", revision])
        # the filename is the last argument
        command.append(self.location_abs)
        exitcode, output, error = run_command(command)
        if exitcode != 0:
            raise IOError("[P4] Perforce error running '%s': %s" \
                    % (command, error))
        return output

