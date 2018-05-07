from .archiveit_collection import ArchiveItCollection, ArchiveItCollectionException
from .timemap import convert_LinkTimeMap_to_dict, MalformedLinkFormatTimeMap

__all__ = [ "ArchiveItCollection", "ArchiveItCollectionException",
    "convert_LinkTimeMap_to_dict", "MalformedLinkFormatTimeMap"
]

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())