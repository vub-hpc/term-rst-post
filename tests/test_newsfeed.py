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
Unit tests for term_rst_post.newsfeed

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import os
import pytest

from term_rst_post import newsfeed


@pytest.mark.parametrize(
    'test_url',
    [
        ('http://example.com/index.html', 'http://example.com/index.html'),
        ('http://example.com/', 'http://example.com/'),
        ('http://example.com', 'http://example.com/'),
    ],
)
def test_valid_url(test_url):
    example_url, reference_url = test_url
    parsed_url = newsfeed.valid_url(example_url)
    assert parsed_url.geturl() == reference_url


def test_get_top_ablog_news(exampledir):
    reference_result = {
        'title': 'Test news item',
        'date': '01/01/2021',
        'html_link': '../../../news/2021/test/',
    }

    example_newsfeed = os.path.join(exampledir, 'ablog_newsfeed.html')
    with open(example_newsfeed) as testfile:
        assert newsfeed.get_top_ablog_news(testfile) == reference_result
