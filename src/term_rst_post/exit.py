#
# Copyright 2021-2021 Vrije Universiteit Brussel
#
# This file is part of term-rst-post,
# originally created by the HPC team of Vrije Universiteit Brussel (https://hpc.vub.be),
# with support of Vrije Universiteit Brussel (https://www.vub.be),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/vub-hpc/term-rst-post
#
# term-rst-post is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v3.
#
# term-rst-post is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this code.  If not, see <http://www.gnu.org/licenses/>.
#
##
"""
Exit handler for term-rst-post

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import logging
import sys

logger = logging.getLogger()


def error_exit(message, exc=None):
    """
    Graceful exit on error
    - message: (string) custom error message
    - exc: (Exception) optional exception of the error
    """
    if exc:
        error_message = "{}: {}".format(message, exc)
    else:
        error_message = "{}".format(message)

    logger.error(error_message)
    logging.shutdown()

    logger.debug('Aborting')
    sys.exit(1)
