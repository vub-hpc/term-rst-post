# Term RST Post

Convert documents in reStructuredText (RST) to text files suitable to be displayed in a terminal shell. The text files are formatted using a mixture of ANSI escape codes and markdown. It is also possible to wrap the resulting text to an arbitrary column width.

## Features

### rst2ansi

Converter of RST documents to text files formatted with markdown and ANSI escape codes

* Custom docutils *translator* to text files with ANSI escape codes
* Wrapper of text files that is aware of escape characters (``--wrap``)
* Supported RST elements:
  * title: markdown title plus ANSI bold text
  * subtitle: markdown title
  * section: markdown paragraphs
  * strong: ANSI bold text
  * emphasis: ANSI underline text
  * literal: markdown literal plus ANSI inverse text
  * reference: markdown links
  * bullet list: markdown unordered list
  * enumerated list: markdown unordered list
* Support for custom substitutions:
  * ``|Warning|``: ANSI red background
  * ``|Info|``: ANSI green background
  * other substitutions will be converted to plain text
* Support for [ABlog's update directive](https://ablog.readthedocs.io/manual/posting-and-listing/#directive-update)

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

* Python >=3.6
* ablog >=0.10.0
* sphinx
* docutils
* beautifulsoup4
* (tests) pytest

## Example

The following command will convert the [example RST file with all supported elements](tests/examples/ablog_newspost_complete.rst) into a [text file with ANSI escape codes](tests/references/ablog_newspost_complete.ansi) (display the text file in your terminal).

```
$ rst2ansi tests/examples/ablog_newspost_complete.rst
```

The following example generates a MOTD considering the given HTML news feed of ABlog. New MOTD will be stored in the default file called ``news.motd``.  Any news item converted to MOTD will have an additional header, footer and link. In this case the root directory with RST files will be automatically determined from the news feed HTML file.

```
$ news2motd _website/posts/tag/motd/index.html
  --briefing
  --motd-header motd/_templates/motd-head.ansi
  --motd-footer motd/_templates/motd-foot.ansi
  --ablog-url http://example.com/
```

