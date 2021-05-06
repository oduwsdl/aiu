[![Build Status](https://travis-ci.org/oduwsdl/aiu.svg?branch=master)](https://travis-ci.org/oduwsdl/aiu)

# AIU

AIU is a Python library for extracting information from web archive collections. The work is done through different classes, each specific to a different web archive collection host. Each class performs screen-scraping and API analysis (if available) in order to acquire general collection metadata, seed lists, and seed metadata.

## Installation

This package requires Python 3 and is called `aiu` on PyPI. Installation is handled via `pip`:

`pip install aiu`

## Using the `ArchiveItCollection` class

The class named `ArchiveItCollection` has many methods for extracting information about an Archive-It collection using its collection identifier.

For example, to use iPython to get information about Archive-It collection number 5728, one can execute the following:

```
In [1]: from aiu import ArchiveItCollection

In [2]: aic = ArchiveItCollection(5728)

In [3]: aic.get_collection_name()
Out[3]: 'Social Media'

In [4]: aic.get_collectedby()
Out[4]: 'Willamette University'

In [5]: aic.get_description()
Out[5]: 'Social media content created by Willamette University.'

In [6]: aic.get_collection_uri()
Out[6]: 'https://archive-it.org/collections/5728'

In [7]: aic.get_archived_since()
Out[7]: 'Apr, 2015'

In [8]: aic.is_private()
Out[8]: False

In [9]: len(aic.list_seed_uris())
Out[9]: 113

In [10]: aic.list_seed_uris()[0]
Out[10]: 'http://blog.willamette.edu/mba/'

In [11]: seed_url = aic.list_seed_uris()[0]

In [12]: aic.get_seed_metadata(seed_url)
Out[12]:
{'collection_web_pages': [{'title': 'Willamette MBA Blog',  
   'description': ['Blog for the Willamette University Atkinson Graduate School of Management']}]}

```

From this session we now know that the collection's name is _Social Media_, it was collected by _Willamette University_, it has been archived since _April 2015_, it is not private, and it has 113 seeds.

Examine the source in `aiu/archiveit_collection.py` for a full list of methods to use with this class.

## Using the `TroveCollection` class

The class named `TroveCollection` has many methods for extracting information about a [National Library of Australia (NLA)](https://www.nla.gov.au/) [Trove](https://trove.nla.gov.au/website) collection using its collection identifier. **Note: Because NLA has different collection policies than Archive-It, not all methods, or their outputs, are mirrored between `TroveCollection` and `ArchiveItCollection`.**

For example, to use iPython to get information about Trove collection number 13742, one can execute the following:

```
In [1]: from aiu import TroveCollection

In [2]: tc = TroveCollection(13742)

In [3]: tc.get_collection_name()
Out[3]: 'Iconic Australian Brands'

In [4]: tc.get_collectedby()
Out[4]:
{'National Library of Australia': 'http://www.nla.gov.au/',
 'State Library of Queensland': 'http://www.slq.qld.gov.au/'}

In [5]: tc.get_archived_since()
Out[5]: 'Feb 2000'

In [6]: tc.get_archived_until()
Out[6]: 'Mar 2021'

In [7]: len(tc.list_seed_uris())
Out[7]: 64

In [8]: tc.get_breadcrumbs()
Out[8]: [0, 15023]

```

From this session we now know that the collection's name is _Iconic Australian Brands_, it was collected by _National Library of Australia_ and _State Library of Queensland_, has been archived since _Feb 2000_, and contains mementos up to _Mar 2021_, it has 63 seeds, and is a subcollection of collections with identifiers of 0 and 15023 -- the breadcrumbs that lead to this collection.

Examine the source in `aiu/trove_collection.py` for a full list of methods to use with this class.

## Using the `PandoraCollection` class

The class named `PandoraCollection` has many methods for extracting information about a [National Library of Australia (NLA)](https://www.nla.gov.au/) [Pandora](http://pandora.nla.gov.au/) collection using its collection identifier. **Note: Because NLA has different collection policies than Archive-It, not all methods, or their outputs, are mirrored between `TroveCollection` and `ArchiveItCollection` and `PandoraCollection`.**

For example, to use iPython to get information about Pandora collection number 12022, one can execute the following:
```
In [1]: from aiu import PandoraCollection

In [2]: pc = PandoraCollection(12022)

In [3]: pc.get_collection_name()
Out[3]: 'Fact sheets (Victoria. EPA Victoria) - Australian Internet Sites'

In [4]: pc.get_title_pages()
Out[4]:
{'136318': ('https://webarchive.nla.gov.au/tep/136318', 'Air'),
 '136347': ('https://webarchive.nla.gov.au/tep/136347',
  'How to reduce noise from your business'),
 '136317': ('https://webarchive.nla.gov.au/tep/136317', 'Land'),
 '136346': ('https://webarchive.nla.gov.au/tep/136346', 'Landfill gas'),
 '136314': ('https://webarchive.nla.gov.au/tep/136314', 'Litter'),
 '136316': ('https://webarchive.nla.gov.au/tep/136316',
  'Noise (EPA fact sheet)'),
 '136319': ('https://webarchive.nla.gov.au/tep/136319', 'Odour'),
 '136312': ('https://webarchive.nla.gov.au/tep/136312', 'Waste'),
 '136313': ('https://webarchive.nla.gov.au/tep/136313', 'Water')}

In [5]: len(pc.list_memento_urims())
Out[5]: 10

In [6]: pc.list_seed_uris()
Out[6]:
['http://www.epa.vic.gov.au/~/media/Publications/1465.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1481.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1466.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1479.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1486%201.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1467.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1468.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1469.pdf',
 'http://www.epa.vic.gov.au/~/media/Publications/1470.pdf']

In [7]: pc.get_collectedby()
Out[7]: {'State Library of Victoria': 'http://www.slv.vic.gov.au/'}

```

Examine the source in `aiu/pandora_collection.py` for a full list of methods to use with this class.

## Using the `PandoraSubject` class

The class named `PandoraSubject` has many methods for extracting information about a [National Library of Australia (NLA)](https://www.nla.gov.au/) [Pandora](http://pandora.nla.gov.au/) subject using its subject identifier. **Note: Because NLA has different collection policies than Archive-It, not all methods, or their outputs, are mirrored between `TroveCollection` and `ArchiveItCollection` and `PandoraCollection` and `PandoraSubject`.**

For example, to use iPython to get information about Pandora subject number 83, one can execute the following:
```
In [1]: from aiu import PandoraSubject

In [2]: ps = PandoraSubject(83)

In [3]: ps.get_subject_name()
Out[3]: 'Humanities'

In [4]: len(ps.get_title_pages())
Out[4]: 71

In [5]: len(ps.list_memento_urims())
Out[5]: 246

In [6]: len(ps.list_seed_uris())
Out[6]: 71

In [7]: ps.subject_id
Out[7]: '83'

In [8]: ps.get_collectedby()
Out[8]:
{'National Library of Australia': 'http://www.nla.gov.au/',
 'Australian Institute of Aboriginal and Torres Strait Islander Studies': 'http://www.aiatsis.gov.au',
 'State Library of New South Wales': 'http://www.sl.nsw.gov.au/',
 'State Library of Victoria': 'http://www.slv.vic.gov.au/',
 'State Library of Western Australia': 'http://www.slwa.wa.gov.au/',
 'State Library of South Australia': 'http://www.slsa.sa.gov.au/'}

In [9]: ps.list_subcategories()
Out[9]: ['84', '85', '86']
 
```

Examine the source in `aiu/pandora_collection.py` for a full list of methods to use with this class.
