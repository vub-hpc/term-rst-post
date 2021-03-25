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
Converter of documents in RST format to text files with ANSI escape codes.
Supported tags: title, section, strong, emphasis, literal, reference, bullet_list, enumerated_list
Supported substitutions: |Warning|, |Info|

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import logging

from ablog.post import UpdateDirective
from docutils import core, frontend, languages, nodes, parsers, readers, transforms, utils, writers

from term_rst_post.exit import error_exit
from term_rst_post.filetools import resolve_path

logger = logging.getLogger()


class MOTDSubstitutions(transforms.Transform):
    """
    Hook for transform step to replace any undefined substitutions
    This is necessary because we are parsing a single document, while substitutions can be defined elsewhere.
    """

    # Run before the default Substitutions
    default_priority = 210

    def apply(self):
        logger.debug("Applying custom MOTD transforms in docutils document reader")
        known_subs = set(self.document.substitution_defs)
        # GO through tree of substitutions
        for ref in self.document.traverse(nodes.substitution_reference):
            refname = ref['refname']
            if refname not in known_subs:
                # Replace any undefined substitution with an inline element
                # Don't use basic Text element to be able to process these elements later on
                reflabel = f" {refname} "
                ref.replace_self(nodes.inline(reflabel, reflabel))
                logger.debug("Replaced undefined substitution '{}' with inline element".format(ref.astext()))


class MOTDReader(readers.Reader):
    """
    Hook for reader step adding custom transform
    """

    def get_transforms(self):
        default = readers.Reader.get_transforms(self)
        return default + [MOTDSubstitutions]


class ANSICodeWriter(writers.Writer):
    """
    Custom writer based on the markdown writer that outputs ANSI escape codes
    """

    # Formats this writer supports
    supported = ('ansicode',)

    # Final translated form of `document`
    output = None

    def __init__(self, briefing=False):
        """
        Set custom ANSICode translator to the writer
        - briefing: (boolean) Limit translation to a single paragraph
        """
        writers.Writer.__init__(self)
        self.translator_class = ANSICodeTranslator
        self.briefing = briefing

    def translate(self):
        visitor = self.translator_class(self.document, briefing=self.briefing)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class ANSICodeTranslator(nodes.NodeVisitor):
    """
    Custom document translator to ANSI escape code
    The whole document will be translated unless 'briefing' is True. In such a case:
     - the translation is limited to the first paragraph inside the first section
     - all paragraphs inside update directives before that first main paragraph are included
    """

    def __init__(self, document, briefing=False):
        """
        Initialize ANSICode translator
        - briefing: (boolean) Limit translation to a single paragraph
        """
        logger.debug("Using custom ANSICode translator with docutils document writer")

        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)

        self.head = []
        self.body = []

        self.section_level = 0

        self.brief_translation = briefing
        self.beyond_limit = False
        self.first_main_paragraph = None

        # Identify main paragraph of the document to limit translation
        if self.brief_translation:
            error_msg = "RST document is not suitable for single paragraph conversion, {} not found"

            first_section_index = document.first_child_matching_class(nodes.section)
            if first_section_index:
                self.first_section = document[first_section_index]
                logger.debug(f"Found first section of the document with index {first_section_index}")

                first_paragraph_index = self.first_section.first_child_matching_class(nodes.paragraph)
                if first_paragraph_index:
                    self.first_main_paragraph = self.first_section[first_paragraph_index]
                    logger.debug(f"Found main paragraph of the document with index {first_paragraph_index}")
                else:
                    error_exit(error_msg.format("paragraph inside first section"))
            else:
                error_exit(error_msg.format("main section element"))

        # ANSI Escape Codes
        self.defs = {
            'emphasis': ('\033[4m', '\033[24m'),  # Underline on/off
            'strong': ('\033[1m', '\033[22m'),  # Bold on/off
            'literal': ('\033[7m`', '`\033[27m'),  # Inverse on/off and backquotes
            'warning': ('\033[1;31;7m', '\033[0;27m'),  # Red badge on/off
            'info': ('\033[1;32;7m', '\033[0;27m'),  # Green badge on/off
            'update': ('\033[7m', '\033[27m'),  # Inverse on/off
            'problematic': ('\n!!!\n', '\n!!!\n'),
        }

        self.badges = ['Warning', 'Info']

    # Utility methods
    def astext(self):
        """Return the final formatted document as a string."""
        return ''.join(self.head + self.body)

    def ensure_eol(self):
        """Ensure the last line in body is terminated by new line."""
        if self.body and self.body[-1][-1] != '\n':
            self.body.append('\n')

    # Supported inline node elements
    def visit_Text(self, node):
        if not self.beyond_limit:
            text = node.astext()
            self.body.append(text)

    def depart_Text(self, node):
        pass

    def visit_emphasis(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['emphasis'][0])

    def depart_emphasis(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['emphasis'][1])
            logger.debug("Translated emphasis element to ANSICode: '{}'".format(node.astext()))

    def visit_strong(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['strong'][0])

    def depart_strong(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['strong'][1])
            logger.debug("Translated strong element to ANSICode: '{}'".format(node.astext()))

    def visit_literal(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['literal'][0])

    def depart_literal(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['literal'][1])
            logger.debug("Translated literal element to ANSICode: '{}'".format(node.astext()))

    def visit_reference(self, node):
        """ Encapsulate links with names """
        if not self.beyond_limit:
            if 'name' in node.attributes:
                self.body.append('[')

    def depart_reference(self, node):
        """ Encapsulate links with names """
        if not self.beyond_limit:
            if 'name' in node.attributes:
                self.body.append(']({})'.format(node.attributes['refuri']))
                logger.debug("Translated non-explicit link element to markdown: '{}'".format(node.astext()))

    def visit_inline(self, node):
        """ Badges use inline elements"""
        if not self.beyond_limit:
            for badge in self.badges:
                if badge in node.astext():
                    self.body.append(self.defs[badge.lower()][0])

    def depart_inline(self, node):
        """ Badges use inline elements"""
        if not self.beyond_limit:
            for badge in self.badges:
                if badge in node.astext():
                    self.body.append(self.defs[badge.lower()][1])
                    logger.debug("Translated badge element to ANSICode: '{}'".format(node.astext()))

    def visit_problematic(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['problematic'][0])

    def depart_problematic(self, node):
        if not self.beyond_limit:
            self.body.append(self.defs['problematic'][1])

    # Supported block node elements
    def visit_paragraph(self, node):
        if not self.beyond_limit and not isinstance(node.parent, nodes.list_item):
            # Ensure spacing for paragraphs not in lists
            self.ensure_eol()
            self.body.append('\n')

    def depart_paragraph(self, node):
        if not self.beyond_limit:
            self.body.append('\n')

            if self.brief_translation and node == self.first_main_paragraph:
                # Stop translation after end of first main paragraph
                self.beyond_limit = True

    def visit_bullet_list(self, node):
        if not self.beyond_limit:
            self.body.append('\n')

    def depart_bullet_list(self, node):
        pass

    def visit_enumerated_list(self, node):
        if not self.beyond_limit:
            self.body.append('\n')

    def depart_enumerated_list(self, node):
        pass

    def visit_list_item(self, node):
        if not self.beyond_limit:
            self.body.append(' * ')
            logger.debug("Translated list item to markdown: '{}'".format(node.astext()))

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_title(self, node):
        """ Main title and section titles """
        if not self.beyond_limit:
            self.ensure_eol()
            if self.section_level == 0:
                self.head.append('\n{}# '.format(self.defs['strong'][0]))
            else:
                self.body.append(
                    '\n{}{} '.format(
                        self.defs['strong'][0],
                        self.section_level * '#',
                    )
                )

    def depart_title(self, node):
        if not self.beyond_limit:
            self.body.append('{}\n'.format(self.defs['strong'][1]))
            logger.debug("Translated title element to markdown: '{}'".format(node.astext()))

    def visit_subtitle(self, node):
        """ Subtitles in the main document tree """
        if not self.beyond_limit:
            if isinstance(node.parent, nodes.document):
                self.body.append('{} '.format((self.section_level + 1) * '#'))
                logger.debug("Translated subtitle element to markdown: '{}'".format(node.astext()))
            else:
                raise nodes.SkipNode

    def visit_UpdateNode(self, node):
        """ ABlog update directive """
        if not self.beyond_limit:
            self.body.append(
                '\n{0} Update {1} {2}'.format(
                    self.defs['update'][0],
                    node.attributes['date'],
                    self.defs['update'][1],
                )
            )

    def depart_UpdateNode(self, node):
        """ ABlog update directive """
        if not self.beyond_limit:
            self.body.append('\n')
            logger.debug("Translated ABlog update directive to ANSICode: '{}'".format(node.astext()))

    def visit_transition(self, node):
        """Replace a transition by a horizontal rule"""
        if not self.beyond_limit:
            self.body.append('\n---\n\n')
            raise nodes.SkipNode

    # Irrelevant Nodes
    def visit_docinfo(self, node):
        """ Ignore anything in docinfo """
        raise nodes.SkipNode

    def visit_field_list(self, node):
        """ Ignore anything in header field list """
        raise nodes.SkipNode

    def visit_system_message(self, node):
        """Keep output document clean"""
        pass

    def depart_system_message(self, node):
        """Keep output document clean"""
        pass

    def default_visit(self, node):
        """Default node visit method"""
        pass

    def default_departure(self, node):
        """Default node depart method"""
        pass

    def unknown_visit(self, node):
        """Ignore unknown elements"""
        pass

    def unknown_departure(self, node):
        """Ignore unknown elements"""
        pass


def make_ansicode_from_rst(ansicode_filename, rst_filename, briefing=False):
    """
    Convert document in RST to text using ANSI escape code
    - ansicode_filename: (string) Path of text file with ANSI escape code
    - rst_filename: (string) Path of RST file
    - briefing: (boolean) Limit conversion to a single paragraph
    """
    # Add update directive from ablog
    parsers.rst.directives.register_directive('update', UpdateDirective)

    # Publish document with custom MOTD reader and ANSICode writer
    try:
        source = open(rst_filename, 'r')
    except IOError as err:
        error_exit("News RST file not found: '{}'".format(rst_filename), err)
    else:
        logger.debug("Opened file with read access: '{}'".format(rst_filename))

    try:
        destination = open(ansicode_filename, 'x')
    except IOError as err:
        error_exit("Failed to create text ANSI file: '{}'".format(ansicode_filename), err)
    else:
        logger.debug("Opened file with write access: '{}'".format(ansicode_filename))

    core.publish_file(
        source=source,
        destination=destination,
        reader=MOTDReader(),
        writer=ANSICodeWriter(briefing=briefing),
    )
    logger.info("Converted RST document to ANSI Escape Code: '{}'".format(ansicode_filename))

    try:
        source.close()
        destination.close()
    except IOError as err:
        error_exit("Failed to close opened files", err)


def get_post_info_from_rst(rst_file):
    """
    Parse RST file and return date from its docinfo field list
    - rst_file: (file object) Path of RST file
    """
    post = {'source': resolve_path(rst_file.name)}

    # Add update directive from ablog
    parsers.rst.directives.register_directive('update', UpdateDirective)

    # Traverse RST document tree and retrieve post title and date
    rst_doctree = core.publish_doctree(rst_file.read(), reader=MOTDReader())

    try:
        title = rst_doctree.traverse(nodes.title)
        post['title'] = list(title)[0].astext()
    except IndexError:
        raise IndexError(f"Malformed RST news post file, missing title: '{rst_file.name}'")

    for field in rst_doctree.traverse(nodes.field):
        field_name = field.first_child_matching_class(nodes.field_name)
        if field[field_name].astext() == 'date':
            field_body = field.first_child_matching_class(nodes.field_body)
            post['date'] = field[field_body].astext()
            logger.info("Found RST news post from {}: '{}'".format(post['date'], post['title']))
            return post

    raise ValueError(f"Malformed RST news post file, missing date: '{rst_file.name}'")
