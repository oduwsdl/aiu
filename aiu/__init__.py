from .archiveit_collection import ArchiveItCollection, ArchiveItCollectionException
from .trove_collection import TroveCollection, TroveCollectionException
from .pandora_collection import PandoraCollection, PandoraSubject, PandoraCollectionException
from .timemap import convert_LinkTimeMap_to_dict, MalformedLinkFormatTimeMap
from .archive_information import generate_raw_urim
from .utils import generate_archiveit_urits, process_timemaps_for_mementos, discover_raw_urims, get_uri_responses
from .version import name, version, user_agent_string


__all__ = [ "ArchiveItCollection", "ArchiveItCollectionException",
    "convert_LinkTimeMap_to_dict", "MalformedLinkFormatTimeMap",
    "generate_raw_urim", "generate_archiveit_urits", "process_timemaps_for_mementos",
    "discover_raw_urims", "get_uri_responses", "version", "name", "user_agent_string", "TroveCollection", "PandoraCollection", "PandoraSubject" ]

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
