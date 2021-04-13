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
Parser of ABlog feeds in HTML format.

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import argparse
import logging

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit

from term_rst_post.exit import error_exit

logger = logging.getLogger()


def valid_url(url):
    """
    Validate URL passed through argparse
    URL will be structured as <scheme>://<netloc>/<path>?<query>#<fragment>
    - url: (string) URL
    """
    try:
        parsed_url = urlsplit(url)
    except ValueError as err:
        errmsg = f"Invalid URL '{url}': {err}"
        raise argparse.ArgumentTypeError(errmsg)
    else:
        # Fill in the URL path if empty
        if not parsed_url.path:
            pathed_url = urlunsplit(parsed_url[:2] + ('/', '', ''))
            parsed_url = urlsplit(pathed_url)
        # Require scheme and netloc
        if parsed_url.scheme and parsed_url.netloc:
            return parsed_url
        else:
            errmsg = f"Malformed URL '{url}': protocol and/or domain missing"
            raise argparse.ArgumentTypeError(errmsg)


def get_top_ablog_news(newslist):
    """
    Parse list of news in ABlog feed and retrieve top item's date and file path
    News items are identified by their H2 element
    - newslist: (file) HTML document
    """
    try:
        data = newslist.read()
    except ValueError as err:
        error_exit("Cannot read file '{}'".format(newslist.name), err)
    else:
        logger.debug("Read contents of file '{}'".format(newslist.name))

    soup = BeautifulSoup(data, 'html.parser')

    # Select top news item
    try:
        motd_tag = soup.find('h2')
        motd = {
            'title': motd_tag.a.string,
            'html_link': motd_tag.a['href'],
            'date': motd_tag.parent.find('li').i.next_sibling.strip(),
        }
    except AttributeError:
        raise AttributeError(f"Malformed HTML newsfeed from ABlog, missing news header (H2): '{newslist.name}'")
    else:
        logger.info("Found MOTD news entry from {}: '{}'".format(motd['date'], motd['title']))

    return motd
