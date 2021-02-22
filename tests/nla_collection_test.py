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
        session.close()	

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


    def test_list_seed_URIs_11676(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()
        aic = aiu.NLACollection(11676, session=session, logger=logger)
        seed_uris = aic.list_seed_uris()
        self.assertEqual(seed_uris, ['http://boom09.com.au/', 'http://www.socialinclusion.sa.gov.au/files/DiggingDeep.pdf', 'http://kimberleydirectaction.wordpress.com/', 'http://miningcommunities.com.au/', 'http://www.miningfm.com.au/', 'http://www.roxbydowns.com', 'https://trackingonslow.com/'])


    def test_list_memento_urims_11676(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()
        aic = aiu.NLACollection(11676, session=session, logger=logger)
        memento_urims = aic.list_memento_urims()
        self.assertEqual(memento_urims, ['http://pandora.nla.gov.au/pan/116281/20100210-1221/boom09.com.au/index.html', 'http://pandora.nla.gov.au/pan/135435/20120803-1636/www.socialinclusion.sa.gov.au/files/DiggingDeep.pdf', 'http://pandora.nla.gov.au/pan/129256/20140106-1941/kimberleydirectaction.wordpress.com/index.html', 'http://pandora.nla.gov.au/pan/133943/20120905-0000/miningcommunities.com.au/news/index.html', 'http://pandora.nla.gov.au/pan/136485/20130116-0006/www.miningfm.com.au/index.html', 'http://pandora.nla.gov.au/pan/134289/20120605-0000/www.roxbydowns.com/index.html', 'http://pandora.nla.gov.au/pan/153227/20150902-1834/trackingonslow.com/index.html'])