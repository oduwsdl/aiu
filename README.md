[![Build Status](https://travis-ci.org/oduwsdl/archiveit_utilities.svg?branch=master)](https://travis-ci.org/oduwsdl/archiveit_utilities)

# Archive-It Utilities

Archive-It Utilties is a Python library for extracting information from Archive-It collections. Most work is currently done through a single class `ArchiveItCollection`, which performs screen-scraping in order to acquire general collection metadata, seed lists, and seed metadata.

## Installation

This package requires Python 3 and is called `aiu` on PyPI. Installation is handled via `pip`:

`pip install aiu`

## Using the `ArchiveItCollection` class

The heart of Archive-It Utilities is a class named `ArchiveItCollection` that has many methods for extracting information about an Archive-It collection using its collection identifier.

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
