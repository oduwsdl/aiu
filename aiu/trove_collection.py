# -*- coding: utf-8 -*-

"""
aiu.trove_collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module acquires data about an NLA trove collection from the JSON https://webarchive.nla.gov.au/bamboo-service/collection/{collection_id}

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


collection_json_prefix = "https://webarchive.nla.gov.au/bamboo-service/collection/"

trove_prefix ="https://webarchive.nla.gov.au"

class TroveCollectionException(Exception):
    """An exception class to be used by the functions in this file so that the
    source of error can be detected.
    """
    pass

def extract_main_collection_data(res):
    """Obtain general collection metadata different types of Trove collections contains using the json response.
    """
    data = {}
    
    try:
        json_data = json.loads(res.text)
        data["exists"] = True
    except Exception as e:
        try:
            #HTTP ERROR 500 Problem accessing /bamboo-service/collection/12323. Reason: Server Error
            if "Problem accessing /bamboo-service/collection/" in res.text:
                data["exists"] = False
                return data
            else:
                raise ValueError("Could not find 'Problem accessing /bamboo-service/collection/' string in response")

        except IndexError as e:
            logger.error("Failed to find collection name using screen scraping")
            logger.error("Failed to determine if collection does not exist using screen scraping")
            logger.error(metadata_tags)
            raise e
    #For all levels: Mandotory
    data["name"] = json_data["name"] 
    data["collection_uri"] = json_data["collectionUrl"]  
    agencies = json_data["agencies"]
 

    #SUBCOLLECTIONS
    subcollections = json_data["subcollections"]
    subcollection_ids = []
    for id in range(0,len(subcollections)):
        sc_id = subcollections[id]["id"]
        subcollection_ids.append(sc_id)    
    data["subcollections"] = subcollection_ids

    #BREADCRUMBS
    breadcrumbs = json_data["breadcrumbs"]
    breadcrumb_ids = []
    for b_id in range(0,len(breadcrumbs)):
        c_id = breadcrumbs[b_id]["id"]
        breadcrumb_ids.append(c_id)
    data["breadcrumbs"] = breadcrumb_ids

    #MEMENTOS & SEEDS
    snapshots = json_data["snapshots"]
    urims = []
    seed_uris = []
    for m_id in range(0,len(snapshots)):    #
        memento = snapshots[m_id]
        rel_urim = memento["snapshotviewurl"]
        urim = trove_prefix + rel_urim
        gathered_url = memento["gatheredUrl"]
        urims.append(urim)
        seed_uris.append(gathered_url)
    data["seed_uris"]  = seed_uris
    data["urims"]  = urims

    #For all levels: Optional
    data["archived_since"] = "unknown"
    data["archived_until"] = "unknown"
    data["institution_info"] = {}
    data["subject"] = "unknown"
    try:
        data["archived_since"] = json_data["startDate"]["monthyear"]
        data["archived_until"] = json_data["endDate"]["monthyear"]
    except:
        pass
    try:
        if len(breadcrumbs) == 1:
            data["subject"] = data["name"]
        else:
            data["subject"] = breadcrumbs[1]["name"] 
    except:
        pass
    try:
        agency = {}
        for p_id in range(0,len(agencies)):
            name = agencies[p_id]["name"]   
            uri = agencies[p_id]["url"]
            agency[name] = uri
        data["institution_info"] = agency      
    except:
        pass
    return data 




class TroveCollection:
    """Organizes all information acquired about the NLA Trove collection."""

    def __init__(self, collection_id, session=requests.Session(), logger=None):

        self.collection_id = str(collection_id)
        self.session = session
        self.metadata_loaded = False
        self.seed_metadata_loaded = False
        self.metadata = {}
        self.seed_metadata = {}
        self.private = None
        self.exists = None

        self.collection_json_uri = "{}/{}".format(collection_json_prefix, collection_id)
 

        self.logger = logger or logging.getLogger(__name__)  
        #self.session.close()

    def load_collection_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """

        if not self.metadata_loaded:
            self.metadata["main"] = extract_main_collection_data(self.session.get(self.collection_json_uri))
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


    def get_collection_uri(self):
        """Getter for the collection URI, as constructed."""

        self.load_collection_metadata()
        #https%3A%2F%2Fwebarchive.nla.gov.au%2Fcollection%2F15003
        #Should we return the value as extracted or fix the encoding?
        return self.metadata["main"]["collection_uri"]

    def get_subject(self):
        """Getter for the collection's topics, collection name of the superclass"""
        
        self.load_collection_metadata()
        return self.metadata["main"]["subject"]

    def get_archived_since(self):
        """Getter for the collection's archived since field"""

        self.load_collection_metadata()
        return self.metadata["main"]["archived_since"]


    def get_archived_until(self):
        """Getter for the collection's archived until field"""

        self.load_collection_metadata()
        return self.metadata["main"]["archived_until"]

    def get_collectedby(self):
        """Getter for the collecting organization's name"""

        self.load_collection_metadata()
        #List of agencies
        return self.metadata["main"]["institution_info"]

    def list_seed_uris(self):
        """Lists the seed URIs of an NLA Trove collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["seed_uris"] 
        
    def list_memento_urims(self):
        """Lists the memento URIMs of an NLA Trove collection."""

        self.load_collection_metadata()
        #print(self.metadata["main"]["urims"])
        return self.metadata["main"]["urims"]

    def get_breadcrumbs(self):
        """Lists the memento URIMs of an NLA Trove collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["breadcrumbs"]

    def get_subcollections(self):
        """Lists the memento URIMs of an NLA Trove collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["subcollections"]      
