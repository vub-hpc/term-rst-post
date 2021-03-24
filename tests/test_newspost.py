#
# Copyright 2021-2021 Vrije Universiteit Brussel
#
# This file is part of term_rst_post,
# originally created by the HPC team of Vrije Universiteit Brussel (https://hpc.vub.be),
# with support of Vrije Universiteit Brussel (https://www.vub.be),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/sisc-hpc/term_rst_post
#
# term_rst_post is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v3.
#
# term_rst_post is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this code.  If not, see <http://www.gnu.org/licenses/>.
#
##
"""
Unit tests for term_rst_post.newspost

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import os
import pytest

from term_rst_post import newspost


@pytest.mark.parametrize(
    'ablog_newspost',
    [
        'ablog_newspost_simple',
        'ablog_newspost_multiparagraph',
        'ablog_newspost_subtitle',
        'ablog_newspost_textformat',
        'ablog_newspost_links',
        'ablog_newspost_subsitutions',
        'ablog_newspost_list',
        'ablog_newspost_richlist',
        'ablog_newspost_update',
        'ablog_newspost_multiupdate',
        'ablog_newspost_richupdate',
        'ablog_newspost_complete',
    ],
)
def test_make_ansicode_from_rst(ablog_newspost, tmpdir, exampledir, refdir):
    example_doc = os.path.join(exampledir, f"{ablog_newspost}.rst")
    test_doc = os.path.join(tmpdir, f"{ablog_newspost}.ansi")
    reference_doc = os.path.join(refdir, f"{ablog_newspost}.ansi")

    newspost.make_ansicode_from_rst(test_doc, example_doc)

    with open(test_doc, 'r') as testfile:
        test_doc_text = testfile.read()

    with open(reference_doc, 'r') as reffile:
        reference_doc_text = reffile.read()

    assert test_doc_text == reference_doc_text


def test_get_post_info_from_rst(exampledir):
    reference_result = {
        'title': 'Test news post with a simple paragraph',
        'date': '01/01/2021',
    }

    example_doc = os.path.join(exampledir, 'ablog_newspost_simple.rst')
    with open(example_doc, 'r') as testfile:
        post_info = newspost.get_post_info_from_rst(testfile)

    # Filter out untested keys (eg paths)
    post_info = {k: post_info.get(k, None) for k in reference_result}

    assert post_info == reference_result
