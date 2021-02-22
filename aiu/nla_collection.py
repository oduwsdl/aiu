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
    #data["description"] = "No description."
    data["archived_since"] = "unknown"
    data["archived_until"] = "unknown"

    #To identidy the type of collection (supercollection, collection, subcollection)
    subcollections = json_data["subcollections"]
    breadcrumbs = json_data["breadcrumbs"]

    if len(subcollections) == 0:
        #This is a subcollection which contains mementos
        #Breadcrumbs
        breadcrumb = []
        for b_id in range(0,len(breadcrumbs)):
            c_id = breadcrumbs[b_id]["id"]
            breadcrumb.append(c_id)
        data["collection_type"] = ["L3 Subcollection - contains mementos", breadcrumb]
        agencies = json_data["agencies"]
        #agency_info = []
        agency = {}
        for p_id in range(0,len(agencies)):
            name = agencies[p_id]["name"]   
            uri = agencies[p_id]["url"]
            agency[name] = uri
        data["institution_info"] = agency
        #data["institution_uri"] = agency_uris
        data["subject"] = breadcrumbs[1]["name"] #supercollection name
        data["archived_since"] = json_data["startDate"]["monthyear"] #other formats available
        data["archived_until"] = json_data["endDate"]["monthyear"] #other formats available

        #Memento & Seed URI data
        snapshots = json_data["snapshots"]
        seed_uris, urims = get_memento(snapshots)
        data["seed_uris"]  = seed_uris
        data["urims"]  = urims
    else: #This is a supercollection or collection which contains subcollections
        if len(breadcrumbs) == 1:
            #This is a supercollection which contains collections
            breadcrumb = []
            for b_id in range(0,len(breadcrumbs)):
                c_id = breadcrumbs[b_id]["id"]
                breadcrumb.append(c_id)
            data["collection_type"] = ["L1 Supercollection - contains collections",breadcrumb]
            data["subject"] = data["name"] #same as the collection name
            supercollection_seed_uris = []
            supercollection_urims = []
            for sc_id in range(0,len(subcollections)):
                sc_url = subcollections[sc_id]["collectionUrl"] 
                sc_url_id = sc_url.split("/")[2]
                collection_json_uri = collection_json_prefix + sc_url_id
                res = requests.get(collection_json_uri)
                json_data = json.loads(res.text)
                collections = json_data["subcollections"]
                collection_seed_uris, collection_urims = get_subcollections(collections)
                supercollection_seed_uris.extend(collection_seed_uris)
                supercollection_urims.extend(collection_urims)
            #print(supercollection_urims)
            data["seed_uris"]  = supercollection_seed_uris
            data["urims"]  = supercollection_urims            

        if len(breadcrumbs) == 2:
            #This is a collection which contains subcollections 
            breadcrumb = []
            for b_id in range(0,len(breadcrumbs)):
                c_id = breadcrumbs[b_id]["id"]
                breadcrumb.append(c_id)            
            data["collection_type"] = ["L2 Collection - contains subcollections", breadcrumb]
            data["subject"] = breadcrumbs[1]["name"] #supercollection name
            data["archived_since"] = json_data["startDate"]["monthyear"] #other formats available
            data["archived_until"] = json_data["endDate"]["monthyear"] #other formats available
            collection_seed_uris, collection_urims = get_subcollections(subcollections)
            data["seed_uris"]  = collection_seed_uris
            data["urims"]  = collection_urims            
    return data 

def get_subcollections(subcollections):
    collection_seed_uris = []
    collection_urims = []
    for sc_id in range(0,len(subcollections)):
        sc_url = subcollections[sc_id]["collectionUrl"]
        sc_url_id = sc_url.split("/")[2]
        subcollection_json_uri = collection_json_prefix + sc_url_id
        #Making a request to the sub-collection URLs
        res = requests.get(subcollection_json_uri)
        json_data = json.loads(res.text)
        seed_uris, urims = get_memento(json_data["snapshots"])
        collection_seed_uris.extend(seed_uris)
        collection_urims.extend(urims)
    return collection_seed_uris, collection_urims

def get_memento(snapshots):
    urims = []
    seed_uris = []
    for m_id in range(0,len(snapshots)):    #
        memento = snapshots[m_id]
        urim = memento["url"]
        gathered_url = memento["gatheredUrl"]
        urims.append(urim)
        seed_uris.append(gathered_url)
    return seed_uris, urims

class NLACollection:
    """Organizes all information acquired about the NLA collection."""

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

    def get_collection_type(self):
        """Getter for the collection type"""

        self.load_collection_metadata()
        return self.metadata["main"]["collection_type"]

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
        """Lists the seed URIs of an NLA collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["seed_uris"] 
        
    def list_memento_urims(self):
        """Lists the memento URIMs of an NLA collection."""

        self.load_collection_metadata()
        return self.metadata["main"]["urims"]