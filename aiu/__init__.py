from .archiveit_collection import ArchiveItCollection, ArchiveItCollectionException
from .timemap import convert_LinkTimeMap_to_dict, MalformedLinkFormatTimeMap
from .archive_information import generate_raw_urim
from .utils import generate_archiveit_urits, process_timemaps_for_mementos, discover_raw_urims, get_uri_responses

__all__ = [ "ArchiveItCollection", "ArchiveItCollectionException",
    "convert_LinkTimeMap_to_dict", "MalformedLinkFormatTimeMap",
    "generate_raw_urim", "generate_archiveit_urits", "process_timemaps_for_mementos",
    "discover_raw_urims", "get_uri_responses"
]

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())