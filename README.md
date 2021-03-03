[![Build Status](https://travis-ci.org/oduwsdl/aiu.svg?branch=master)](https://travis-ci.org/oduwsdl/aiu)

# AIU (formerly Archive-It Utilities)

AIU is a Python library for extracting information from Archive-It collections. Most work is currently done through a single class `ArchiveItCollection`, which performs screen-scraping in order to acquire general collection metadata, seed lists, and seed metadata.

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

In [5]: aic.get_archived_since()
Out[5]: 'Apr, 2015'

In [6]: aic.is_private()
Out[6]: False

In [7]: seeds = aic.list_seed_uris()

In [8]: len(seeds)
Out[8]: 107
```

From this session we now know that the collection's name is _Social Media_, it was collected by _Willamette University_, it has been archived since _April 2015_, it is not private, and it has 107 seeds.

For now, examine the source in `aiu/archiveit_collection.py` for a full list of methods to use with this class.


## Using the `NLACollection` class

The class named `NLACollection` has many methods for extracting information about an [National Library of Australia (NLA)](https://www.nla.gov.au/) [Trove](https://trove.nla.gov.au/website) collection using its collection identifier. **Note: Because NLA has different collection policies than Archive-It, not all methods, or their outputs, are mirrored between `NLACollection` and `ArchiveItCollection`.**

For example, to use iPython to get information about NLA collection number 13742, one can execute the following:

```
In [1]: from aiu import NLACollection

In [2]: nlac = NLACollection(13742)

In [3]: nlac.get_collection_name()
Out[3]: 'Iconic Australian Brands'

In [4]: nlac.get_collectedby()
Out[4]:
{'National Library of Australia': 'http://www.nla.gov.au/',
 'State Library of Queensland': 'http://www.slq.qld.gov.au/'}

In [5]: nlac.get_archived_since()
Out[5]: 'Feb 2000'

In [6]: nlac.get_archived_until()
Out[6]: 'Mar 2021'

In [7]: aic.is_private()
Out[7]: False

In [8]: seeds = nlac.list_seed_uris()

In [9]: len(seeds)
Out[9]: 63

In [10]: nlac.get_breadcrumbs()
Out[10: [0, 15023]

```

From this session we now know that the collection's name is _Iconic Australian Brands_, it was collected by _National Library of Australia_ and _State Library of Queensland_, has been archived since _Feb 2000_, and contains mementos up to _Mar 2021_, it has 63 seeds, and is a subcollection of collections with identifiers of 0 and 15023 -- the breadcrumbs that lead to this collection.

For now, examine the source in `aiu/nla_collection.py` for a full list of methods to use with this class.
