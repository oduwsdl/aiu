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

class TestPandoraCollection(unittest.TestCase):

    def test_nonexistent_collection(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()        

        aic = aiu.PandoraCollection(112233, session=session, logger=logger)
        self.assertFalse(aic.does_exist())
        session.close() 

    def test_collection_5260(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()       

        aic = aiu.PandoraCollection(5260, session=session, logger=logger)
        name = aic.get_collection_name()
        tep = aic.get_title_pages()
        self.assertEqual(name,"International Year of Mountains, 2002 - Australian Internet Sites")
        self.assertEqual(tep, {'24780': ('https://webarchive.nla.gov.au/tep/24780', 'International Year of Mountains 2002 in Australia'), '24777': ('https://webarchive.nla.gov.au/tep/24777', 'International Year of Mountains fact sheet'), '24781': ('https://webarchive.nla.gov.au/tep/24781', 'International Year of the Mountains')})
        session.close() 

    def test_list_seed_URIs_5260(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()

        aic = aiu.PandoraCollection(5260, session=session, logger=logger)
        seed_uris = aic.list_seed_uris()
        self.assertEqual(seed_uris, ['http://www.australianalps.ea.gov.au/', 'http://www.ea.gov.au/events/iym/index.html', 'http://www.environment.act.gov.au/'])
    
    def test_list_memento_URIMs_5260(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()
        aic = aiu.PandoraCollection(5260, session=session, logger=logger)
        memento_urims = aic.list_memento_urims()
        self.assertEqual(memento_urims,['https://webarchive.nla.gov.au/awa/20020505140000/http://pandora.nla.gov.au/pan/24780/20020506-0000/www.australianalps.ea.gov.au/iym.html\n', 'https://webarchive.nla.gov.au/awa/20020507140000/http://pandora.nla.gov.au/pan/24777/20020508-0000/www.ea.gov.au/events/iym/index.html\n', 'https://webarchive.nla.gov.au/awa/20020715140000/http://pandora.nla.gov.au/pan/24781/20020716-0000/www.environment.act.gov.au/ie4/yourenvironmenthwp/iym.html'])


class TestPandoraSubject(unittest.TestCase):

    def test_nonexistent_subject(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()        

        aic = aiu.PandoraSubject(112233, session=session, logger=logger)
        self.assertFalse(aic.does_exist())
        session.close() 

    def test_subject_83(self):
        logger = logging.getLogger(__name__)
        requests_cache.install_cache(cachefile, backend='sqlite')
        session = requests.Session()       

        aic = aiu.PandoraSubject(83, session=session, logger=logger)
        name = aic.get_subject_name()
        #collection_names = aic.get_subject_name()
        # tep = aic.get_title_pages()
        self.assertEqual(name,"Humanities")
        # self.assertEqual(tep, {'24780': ('https://webarchive.nla.gov.au/tep/24780', 'International Year of Mountains 2002 in Australia'), '24777': ('https://webarchive.nla.gov.au/tep/24777', 'International Year of Mountains fact sheet'), '24781': ('https://webarchive.nla.gov.au/tep/24781', 'International Year of the Mountains')})
        session.close() 

    # def test_list_seed_URIs_5260(self):
    #     logger = logging.getLogger(__name__)
    #     requests_cache.install_cache(cachefile, backend='sqlite')
    #     session = requests.Session()

    #     aic = aiu.PandoraCollection(5260, session=session, logger=logger)
    #     seed_uris = aic.list_seed_uris()
    #     self.assertEqual(seed_uris, ['http://www.australianalps.ea.gov.au/', 'http://www.ea.gov.au/events/iym/index.html', 'http://www.environment.act.gov.au/'])
    
    # def test_list_memento_URIMs_5260(self):
    #     logger = logging.getLogger(__name__)
    #     requests_cache.install_cache(cachefile, backend='sqlite')
    #     session = requests.Session()
    #     aic = aiu.PandoraCollection(5260, session=session, logger=logger)
    #     memento_urims = aic.list_memento_urims()
    #     self.assertEqual(memento_urims,['https://webarchive.nla.gov.au/awa/20020505140000/http://pandora.nla.gov.au/pan/24780/20020506-0000/www.australianalps.ea.gov.au/iym.html\n', 'https://webarchive.nla.gov.au/awa/20020507140000/http://pandora.nla.gov.au/pan/24777/20020508-0000/www.ea.gov.au/events/iym/index.html\n', 'https://webarchive.nla.gov.au/awa/20020715140000/http://pandora.nla.gov.au/pan/24781/20020716-0000/www.environment.act.gov.au/ie4/yourenvironmenthwp/iym.html'])



 