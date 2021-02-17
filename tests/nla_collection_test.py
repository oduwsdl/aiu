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

    def test_L1_collection_15003(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()		

        aic = aiu.NLACollection(15003, session=session, logger=logger)
        name = aic.get_collection_name()
        uri = aic.get_collection_uri()
        subject = aic.get_subject()
        collection_type = aic.get_collection_type()

        self.assertEqual(name,"Business & Economy")
        self.assertEqual(uri,"https%3A%2F%2Fwebarchive.nla.gov.au%2Fcollection%2F15003")
        self.assertEqual(subject,"Business & Economy")
        self.assertEqual(collection_type,"L1 Supercollection - contains collections")

    def test_L2_collection_11666(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()		

        aic = aiu.NLACollection(11666, session=session, logger=logger)
        name = aic.get_collection_name()
        uri = aic.get_collection_uri()
        subject = aic.get_subject()
        archived_since = aic.get_archived_since()
        archived_until = aic.get_archived_until()
        collection_type = aic.get_collection_type()

        self.assertEqual(name,"Australia's early 21st century resources boom")
        self.assertEqual(uri,"https%3A%2F%2Fwebarchive.nla.gov.au%2Fcollection%2F11666")
        self.assertEqual(subject,"Business & Economy")
        self.assertEqual(archived_since, "Nov 2006")
        self.assertEqual(archived_until,"Jan 2021")
        self.assertEqual(collection_type,"L2 Collection - contains subcollections")

    def test_L3_collection_11676(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()		

        aic = aiu.NLACollection(11676, session=session, logger=logger)
        name = aic.get_collection_name()
        uri = aic.get_collection_uri()
        subject = aic.get_subject()
        archived_since = aic.get_archived_since()
        archived_until = aic.get_archived_until()
        collected_by = aic.get_collectedby()
        collection_type = aic.get_collection_type()

        self.assertEqual(name,"Communities - cultural, social and local web sites")
        self.assertEqual(uri,"https%3A%2F%2Fwebarchive.nla.gov.au%2Fcollection%2F11676")
        self.assertEqual(subject,"Business & Economy")
        self.assertEqual(archived_since, "Feb 2010")
        self.assertEqual(archived_until,"May 2020")
        self.assertEqual(collected_by, {'State Library of South Australia': 'http://www.slsa.sa.gov.au/', 'State Library of Western Australia': 'http://www.slwa.wa.gov.au/', 'State Library of Queensland': 'http://www.slq.qld.gov.au/', 'National Library of Australia': 'http://www.nla.gov.au/', 'State Library of Victoria': 'http://www.slv.vic.gov.au/'})
        self.assertEqual(collection_type,"L3 Subcollection - contains mementos")