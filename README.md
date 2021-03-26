# Term RST Post

Convert documents in reStructuredText (RST) to text files suitable to be displayed in a terminal shell. The text files are formatted using a mixture of ANSI escape codes and markdown. It is also possible to wrap the resulting text to an arbitrary column width.

## Features

### rst2ansi

Converter of RST documents to text files formatted with markdown and ANSI escape codes

* Custom docutils *translator* to text files with ANSI escape codes
* Wrapper of text files that is aware of escape charcaters (``--wrap``)
* Supported RST elements:
  * title: markdown title plus ANSI bold text
  * subtitle: markdown title
  * section: markdown paragraphs
  * strong: ANSI bold text
  * emphasis: ANSI underline text
  * literal: markdown literal plus ANSI inverse text
  * reference: markdown links
  * bulletr list: markdown unordered list
  * enumerated list: markdown unordered list
* Support for custom substitutions:
  * ``|Warning|``: ANSI red background
  * ``|Info|``: ANSI green background
  * other subsitutions will be converted to plain text
* Support for ABlog's update directive

### news2motd

Parse post documents from ABlog and convert to a text file to be used as *message of the day* (MOTD).

* Same features as ``rst2ansi``
* Convert any RST file with a post from ABlog to text format using ANSI escape codes
* Optionally, parse an HTML file with a feed of posts from ABlog and retrieve a certain post item RST document
* Use the publication date of the post to determine if the post is worth being published as MOTD (``--lifespan``)
* Generate brief MOTD with a single paragraph from RST document (``--briefing``)
* Add additional header or footer sections to the text file (``--motd-header``, ``--motd-footer``)
* Add additional link in the MOTD to the HTML page of the RST document (``--ablog-url``)
* Configure the active MOTD

## Requirements

* Python +3.8
* docutils
* sphinx
* ablog
* beautifulsoup4
* (tests) pytest

## Example

The following command will convert the [example RST file with all supported elements](tests/examples/ablog_newspost_complete.rst) into a [text file with ANSI escape codes](tests/references/ablog_newspost_complete.ansi) (display the text file in your terminal).

```
$ rst2ansi tests/examples/ablog_newspost_complete.rst
```

The following example generates a brief MOTD from some news feed of ABlog and adds an extra header, footer and link. In this case the root directory with RST files will be automatiaclly determined from the news feed HTML file. The command defines the root directory of MOTD text files as ``motd``. The location of the header and footer files can be anywehre else.

```
$ news2motd posts/tag/motd/index.html
  --briefing --motd-dir motd
  --motd-header motd/_templates/motd-head.ansi
  --motd-footer motd/_templates/motd-foot.ansi
  --ablog-url http://example.com/
```

