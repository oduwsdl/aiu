# -*- coding: utf-8 -*-

"""
aiu.pandora_collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module acquires data about an NLA pandora collection.

"""

import os
import json
import requests
import logging
import logging.config
import argparse
import csv
import sys

from io import StringIO

from datetime import datetime
from bs4 import BeautifulSoup

from .version import user_agent_string

logger = logging.getLogger(__name__)


tep_json_prefix = "https://webarchive.nla.gov.au/bamboo-service/tep/"

trove_prefix = "https://webarchive.nla.gov.au"

pandora_col_prefix ="http://pandora.nla.gov.au/col/"

pandora_sub_prefix ="http://pandora.nla.gov.au/subject/"


class PandoraCollectionException(Exception):
    """An exception class to be used by the functions in this file so that the
    source of error can be detected.
    """
    pass

def extract_main_collection_data(soup):
    """Obtain general collection metadata different types of Trove collections contains using the json response.
    """
    data = {}
    try:
        span = soup.find('span', id="selectedTitle")
        data["name"]  = span.text
        data["exists"] = True
    except:
        div = soup.find('div',id="content")
        if "THIS PAGE CANNOT BE FOUND" in div.find_all("h5")[0].get_text():
            data["exists"] = False
            return data  
        else:
            raise IndexError("Could not find 'THIS PAGE CANNOT BE FOUND' string using screen scraping")
    itemlist = soup.find_all('div', {"class": "itemlist"})
    uls = itemlist[0].find('ul')
    tep = {}
    tep_ids = []
    for ul in uls:
        newsoup = BeautifulSoup(str(ul), 'html.parser')
        lis = newsoup.find_all('li')
        for li in lis:
            a_tag = li.find('a')
            tep_href = a_tag['href']
            tep_id = tep_href.split("/")[2]
            tep_url = trove_prefix + tep_href
            text = li.text
            tep_ids.append(tep_id)
            tep[tep_id] = (tep_url,text)
    data["tep"] = tep
    #print(tep)
    seed_uris = []
    urims = []
    main_dic = {}
    for tep_id in tep_ids:
        tep_json_uri = tep_json_prefix + tep_id
        tep_dic = get_metadata_from_tep(requests.get(tep_json_uri),data)
        seed_uri = tep_dic["seed_uri"]
        mementos = tep_dic["urims"]
        urims.extend(mementos) 
        seed_uris.append(seed_uri)

        main_dic[tep_id] = tep_dic
    #print(main_dic)
    data["seed_uris"] = seed_uris
    data["urims"] = urims
    #print(urims)
    return data
    


def get_metadata_from_tep(res,data):
    tep = {}
    try:
        json_data = json.loads(res.text)
        #print(json_data)
        tep["exists"] = True
    except Exception as e:
        try:
            #HTTP ERROR 500 Problem accessing /bamboo-service/tep/12323. Reason: Server Error
            if "Problem accessing /bamboo-service/tep/" in res.text:
                tep["exists"] = False
                return tep
            else:
                raise ValueError("Could not find 'Problem accessing /bamboo-service/collection/' string in response")

        except IndexError as e:
            logger.error("Failed to find collection name using screen scraping")
            logger.error("Failed to determine if collection does not exist using screen scraping")
            logger.error(metadata_tags)
            raise e

    tep["name"] = json_data["name"] 
    tep["tep_uri"] = json_data["tepUrl"]  
    tep["seed_uri"] = json_data["url"]

    #Mementos
    urims = []
    instances = json_data["instances"]
    for each in instances:
        rel_urim = each["snapshotviewurl"]
        urim = trove_prefix + rel_urim
        urims.append(urim)
    tep["urims"]  = urims

    #Institutions
    agencies = json_data["agencies"]
    try:
        agency = {}
        for p_id in range(0,len(agencies)):
            name = agencies[p_id]["name"]   
            uri = agencies[p_id]["url"]
            agency[name] = uri
        tep["institution_info"] = agency      
    except:
        pass
    return tep 



class PandoraCollection:
    """Organizes all information acquired about the Pandora collection."""

    def __init__(self, collection_id, session=requests.Session(), logger=None):

        self.collection_id = str(collection_id)
        self.session = session
        self.metadata_loaded = False
        self.seed_metadata_loaded = False
        self.metadata = {}
        self.seed_metadata = {}
        self.private = None
        self.exists = None

        self.collection_uri = "{}/{}".format(pandora_col_prefix, collection_id)
        self.firstpage_response = self.session.get(self.collection_uri) 

        self.logger = logger or logging.getLogger(__name__)  
        #self.session.close()

    def load_collection_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """
        #print(self.collection_tep_uri)
        if not self.metadata_loaded:
            soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')
            self.metadata["main"] = extract_main_collection_data(soup)
            #self.metadata["optional"] = extract_optional_collection_data(self.session.get(self.collection_json_uri))
            self.metadata_loaded = True

    def does_exist(self):
        """Returns `True` if the collection actually exists and requests for
        its data did not result in HTTP 500*."""

        self.load_collection_metadata()
        return self.metadata["main"]["exists"]  

    def get_collection_name(self):
        """Getter for the collection name, as scraped."""

        self.load_collection_metadata()
        return self.metadata["main"]["name"]

    def get_title_pages(self):
        """Getter for the collection name, as scraped."""

        self.load_collection_metadata()
        return self.metadata["main"]["tep"]

    def list_seed_uris(self):
        """Lists the seed URIs of an NLA Trove collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["seed_uris"] 

    def list_memento_urims(self):
        """Lists the memento URIMs of an NLA Trove collection."""

        self.load_collection_metadata()
        #print(self.metadata["main"]["urims"])
        return self.metadata["main"]["urims"]

def extract_main_subject_data(soup):
    """Obtain general collection metadata different types of Trove collections contains using the json response.
    """
    data = {}
    try:
        title_list = soup.find_all('span', {"class": "selectedTitle"})
        n = len(title_list)
        data["name"]  = title_list[n-1].text
        data["exists"] = True
    except:
        div = soup.find('div',id="content")
        if "THIS PAGE CANNOT BE FOUND" in div.find_all("h5")[0].get_text():
            data["exists"] = False
            return data  
        else:
            raise IndexError("Could not find 'THIS PAGE CANNOT BE FOUND' string using screen scraping")
    # itemlist = soup.find_all('div', {"class": "itemlist"})
    # uls = itemlist[0].find('ul')
    # tep = {}
    # tep_ids = []
    # for ul in uls:
    #     newsoup = BeautifulSoup(str(ul), 'html.parser')
    #     lis = newsoup.find_all('li')
    #     for li in lis:
    #         a_tag = li.find('a')
    #         tep_href = a_tag['href']
    #         tep_id = tep_href.split("/")[2]
    #         tep_url = trove_prefix + tep_href
    #         text = li.text
    #         tep_ids.append(tep_id)
    #         tep[tep_id] = (tep_url,text)
    # data["tep"] = tep
    # #print(tep)
    # seed_uris = []
    # urims = []
    # main_dic = {}
    # for tep_id in tep_ids:
    #     tep_json_uri = tep_json_prefix + tep_id
    #     tep_dic = get_metadata_from_tep(requests.get(tep_json_uri),data)
    #     seed_uri = tep_dic["seed_uri"]
    #     mementos = tep_dic["urims"]
    #     urims.extend(mementos) 
    #     seed_uris.append(seed_uri)

    #     main_dic[tep_id] = tep_dic
    # #print(main_dic)
    # data["seed_uris"] = seed_uris
    # data["urims"] = urims
    # #print(urims)
    return data


class PandoraSubject:
    """Organizes all information acquired about the Pandora subject."""

    def __init__(self, subject_id, session=requests.Session(), logger=None):

        self.subject_id = str(subject_id)
        self.session = session
        self.metadata_loaded = False
        self.seed_metadata_loaded = False
        self.metadata = {}
        self.seed_metadata = {}
        self.private = None
        self.exists = None

        self.subject_uri = "{}/{}".format(pandora_sub_prefix, subject_id)
        self.firstpage_response = self.session.get(self.subject_uri) 

        self.logger = logger or logging.getLogger(__name__)  
        #self.session.close()

    def load_subject_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """
        #print(self.collection_tep_uri)
        if not self.metadata_loaded:
            soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')
            self.metadata["main"] = extract_main_subject_data(soup)
            #self.metadata["optional"] = extract_optional_collection_data(self.session.get(self.collection_json_uri))
            self.metadata_loaded = True

    def does_exist(self):
        """Returns `True` if the collection actually exists and requests for
        its data did not result in HTTP 500*."""

        self.load_subject_metadata()
        return self.metadata["main"]["exists"]  

    def get_subject_name(self):
        """Getter for the collection name, as scraped."""

        self.load_subject_metadata()
        return self.metadata["main"]["name"]

    # def get_title_pages(self):
    #     """Getter for the collection name, as scraped."""

    #     self.load_collection_metadata()
    #     return self.metadata["main"]["tep"]

    # def list_seed_uris(self):
    #     """Lists the seed URIs of an NLA Trove collection."""

    #     self.load_collection_metadata()
    #     return self.metadata["main"]["seed_uris"] 

    # def list_memento_urims(self):
    #     """Lists the memento URIMs of an NLA Trove collection."""

    #     self.load_collection_metadata()
    #     #print(self.metadata["main"]["urims"])
    #     return self.metadata["main"]["urims"]
