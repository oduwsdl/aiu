# -*- coding: utf-8 -*-

import unittest
import logging
import logging.config
import os
import shutil
import zipfile
import pprint
import requests
import requests_cache
import aiu

from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)

cachefile = "{}/test_cache".format(os.path.dirname(os.path.realpath(__file__)))

class TestNLACollection(unittest.TestCase):

    def test_nonexistent_collection(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')

        session = requests.Session()		

        aic = aiu.NLACollection(12345, session=session, logger=logger)
        self.assertFalse(aic.does_exist())