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
Formatting and management of MOTD text files with ANSI escape codes.

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import logging
import os
import re

from textwrap import indent, wrap

from term_rst_post.exit import error_exit

logger = logging.getLogger()


def accomodate_motd(body_file, head_file=None, foot_file=None, foot_link=None, wrap_width=80):
    """
    Transform MOTD text file by: wrapping, indenting and adding header/footer
    - body_file: (file) text file with MOTD body, it will be updated
    - head_file: (file) text file that will be prepended to body
    - foot_file: (file) text file that will be appended to body
    - foot_link: (string) URL for an extra link after the body
    - wrap_width: (int) max column width of the text file
    """
    motd_text = list()
    motd_parts = [part for part in [head_file, body_file, foot_file] if part]
    logger.debug("Parts included in the MOTD: {}".format(', '.join([part.name for part in motd_parts])))

    # Prepend/Append sections to MOTD
    for part in motd_parts:
        try:
            part_text = part.read()
        except IOError as err:
            error_exit(f"Failed to read text file: '{part.name}'", err)
        else:
            motd_text.append(part_text)
            logger.info(f"Added contents of '{part.name}' to ANSI text file")

    # Inject extra link between body and footer
    if foot_link:
        part_link = f"\nMore information in\n{foot_link}\n"
        if foot_file:
            motd_text.insert(-1, part_link)
        else:
            motd_text.append(part_link)

    motd_text = ''.join(motd_text)

    # Check for long URLs
    http_urls = re.findall(r'(https?://[^\s]+)', motd_text)
    for url in http_urls:
        if len(url) > wrap_width:
            logger.warning(f"Found a URL longer than ANSI text width: {url} ({len(url)} char)")

    # Format MOTD text file
    try:
        with open(body_file.name, 'w') as motd_file:
            motd_lines = motd_text.splitlines()
            # Wrap text to default column width respecting spacings and ANSI escape codes
            for n, line in enumerate(motd_lines):
                motd_lines[n : n + 1] = wrap_ansicode(line, wrap_width)
            # Indent with two spaces
            motd_lines = [indent(line, '  ') for line in motd_lines]
            motd_file.write('\n'.join(motd_lines) + '\n')
    except IOError as err:
        error_exit(f"Failed to open ANSI text file to update its contents: '{body_file.name}'", err)
    else:
        logger.info(f"Reformatted contents of ANSI text file '{body_file.name}' to {wrap_width} characters")
        motd_file.close()

    return motd_file


def wrap_ansicode(ansistr, column_width, match_width=5):
    """
    Cuts long text in a single string to a fixed column width accounting for ANSI escape code characters
    - ansistr: (str) text with ANSI escape codes
    - column_width: (int) length of text column in legible charcaters
    - match_width: (int) number of characters used to match between the text with/without ANSI escape codes
    """
    # Text without ANSI escape codes
    clearstr = re.sub('\033\[[0-9;]*m', '', ansistr)

    if len(clearstr) > column_width + 2:
        # Wrap clear string
        clearstr_wrapped = wrap(
            clearstr, width=column_width, replace_whitespace=False, drop_whitespace=False, break_long_words=False
        )

        # number of ANSI escape codes in the text
        ansicodes = len(ansistr) - len(clearstr)
        logger.debug("Wrapping {} characters long line with {} ANSI escape characters".format(len(clearstr), ansicodes))

        # Replicate wrapped lines of clear text with ansi string
        ansistr_wrapped = list()
        for line in clearstr_wrapped:
            # Define zone around end of line at column width of clearstr to find a match point in ansistr
            # 3x `match_width` to the left and `ansicodes` to the right
            cutleft = column_width - (match_width * 3)
            cutright = column_width + ansicodes
            match_zone = ansistr[cutleft:cutright]
            # Find the first matching substring between clearstr and ansistr in this zone
            cutpoint = match_zone.find(line[(match_width * -1) :])
            cutpoint = cutleft + match_width + cutpoint
            # Split ansistr in the same point as clearstr
            leftstr = ansistr[:cutpoint].lstrip()
            ansistr_wrapped.append(leftstr)  # save left part
            ansistr = ansistr[cutpoint:]  # update ansi text with right part
            ansicodes -= len(ansistr_wrapped[-1]) - len(line)  # update number of ANSI codes

        logger.debug(
            "Wrapped long line into {} lines (target is {} lines)".format(len(ansistr_wrapped), len(clearstr_wrapped))
        )
    else:
        ansistr_wrapped = [ansistr]

    return ansistr_wrapped
