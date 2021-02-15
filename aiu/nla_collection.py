# -*- coding: utf-8 -*-

"""
aiu.nla_collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module acquires data about an NLA collection from the JSON https://webarchive.nla.gov.au/bamboo-service/collection/{collection_id}

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

class NLACollectionException(Exception):
    """An exception class to be used by the functions in this file so that the
    source of error can be detected.
    """
    pass

def extract_main_collection_data(res):
    """Obtain general collection metadata different types of NLA collections contains using the json response.
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
    #For all levels
    data["name"] = json_data["name"] 
    data["collection_uri"] = json_data["collectionUrl"]     
    data["description"] = "No description."
    data["archived_since"] = "unknown"
    data["archived_until"] = "unknown"

    #To identidy the type of collection (supercollection, collection, subcollection)
    subcollections = json_data["subcollections"]
    breadcrumbs = json_data["breadcrumbs"]

    if len(subcollections) == 0:
        #This is a subcollection which contains mementos
        agencies = json_data["agencies"]
        agency_names = []
        agency_uris = []
        for p_id in range(0,len(agencies)):
            name = agencies[p_id]["name"]
            uri = agencies[p_id]["url"]
            agency_names.append(name)
            agency_uris.append(uri)
        data["institution_name"] = agency_names
        data["institution_uri"] = agency_uris
        data["subject"] = breadcrumbs[1]["name"] #supercollection name
        data["archived_since"] = json_data["startDate"]["monthyear"] #other formats available
        data["archived_until"] = json_data["endDate"]["monthyear"] #other formats available

    else:       
        #This is a supercollection or collection which contains subcollections
        if len(breadcrumbs) == 1:
            #This is a supercollection which contains collections
            data["subject"] = data["name"] #same as the collection name

        if len(breadcrumbs) == 2:
            #This is a collection which contains subcollections 
            data["subject"] = breadcrumbs[1]["name"] #supercollection name
            data["archived_since"] = json_data["startDate"]["monthyear"] #other formats available
            data["archived_until"] = json_data["endDate"]["monthyear"] #other formats available
    return data

class NLACollection:
    """Organizes all information acquired about the Archive-It collection."""

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
        self.res = self.session.get(self.collection_json_uri)        

        self.logger = logger or logging.getLogger(__name__)  

    def load_collection_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """

        if not self.metadata_loaded:

            # soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')

            self.metadata["main"] = extract_main_collection_data(self.res)
            #self.metadata["optional"] = extract_optional_collection_data(self.res)

            self.metadata_loaded = True

    def does_exist(self):
        """Returns `True` if the collection actually exists and requests for
        its data did not result in 404s or soft-404s."""

        self.load_collection_metadata()

        exists = self.metadata["main"]["exists"]

        #self.logger.debug("exists is set to {}".format(exists))

        return exists          