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

def extract_optional_collection_data(soup):
    """Obtain optional collection metadata different types of NLA collections contains using the json response.
    To be implemented upon testing the general metadata fields first.
    """
    pass

def get_seed_metadata_from_seed_report(collection_id, session):
    """Builds the CSV seed report URI using `collection_id` and saves the
    seed report in `pages_dir`.
    """

    seed_metadata = {}

    seed_report_uri = "https://partner.archive-it.org/api/seed?" \
        "annotate__max=seed_group__name&annotate__max=crawl_definition__recurrence_type" \
        "&collection={}&csv_header=Seed+URL&csv_header=Group&csv_header=Status" \
        "&csv_header=Frequency&csv_header=Type&csv_header=Access&format=csv&" \
        "show_field=url&show_field=seed_group__name&show_field=active&" \
        "show_field=crawl_definition__recurrence_type&show_field=seed_type&" \
        "show_field=publicly_visible&sort=-id".format(collection_id)

    r = session.get(seed_report_uri, headers={'user-agent': user_agent_string})

    seed_report = StringIO(r.text)
    
    csvreader = csv.DictReader(seed_report, delimiter=',')

    for row in csvreader:
    
        seed_metadata[ row["Seed URL"] ] = {} 
        seed_metadata[ row["Seed URL"] ]["group"] = row["Group"]
        seed_metadata[ row["Seed URL"] ]["status"] = row["Status"]
        seed_metadata[ row["Seed URL"] ]["frequency"] = row["Frequency"]
        seed_metadata[ row["Seed URL"] ]["type"] = row["Type"]
        seed_metadata[ row["Seed URL"] ]["access"] = row["Access"]

    return seed_metadata 


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
        self.res = self.session.get(self.collection_uri)        

        self.logger = logger or logging.getLogger(__name__)

    def load_collection_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """

        if not self.metadata_loaded:

            # soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')

            self.metadata["main"] = extract_main_collection_data(res)
            self.metadata["optional"] = extract_optional_collection_data(res)

            self.metadata_loaded = True


    def load_seed_metadata(self):
        """Loads the seed metadata previously downloaded if possible, otherwise
        acquires all collection results pages and parses them for seed metadata.

        This function is separate to limit the number of requests. It should only
        be called if seed metadata is needed.
        """

        #Seeds
        #data["gathered_url"] 
        #What will be metadata?

        self.load_collection_metadata()

        if self.does_exist() is False:
            self.seed_metadata = {}
            return

        if self.is_private() is True:
            self.seed_metadata = {}
            return

        if not self.seed_metadata_loaded:

            timestamp = datetime.now()

            seed_metadata_list = []
            json_data = json.loads(self.res.text) 

            #soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')
            #seed_metadata_list.extend( scrape_seed_metadata(soup) )
            nextpage = scrape_next_page_number(soup)
            result_count = scrape_result_count(soup)

            while nextpage:

                page_uri = "{}/{}/?page={}&totalResultCount={}".format(
                    collection_uri_prefix, self.collection_id, 
                    nextpage, result_count)

                r = self.session.get(page_uri)

                soup = BeautifulSoup(r.text, 'html5lib')

                seed_metadata_list.extend( scrape_seed_metadata(soup) )

                nextpage = scrape_next_page_number(soup)

            for item in seed_metadata_list:
                uri = item["uri"]

                itemdict = {}

                for key in item:
                    if key != "uri":
                        itemdict[key] = item[key]

                self.seed_metadata.setdefault("seeds", {})
                self.seed_metadata["seeds"].setdefault(uri, {})
                self.seed_metadata["seeds"][uri].setdefault(
                    "collection_web_pages", []).append(itemdict)

            seed_report_metadata = get_seed_metadata_from_seed_report(self.collection_id, self.session)
            seed_report_timestamp = datetime.now()

            for uri in seed_report_metadata:
                self.seed_metadata.setdefault("seeds", {})
                self.seed_metadata["seeds"].setdefault(uri, {})
                self.seed_metadata["seeds"][uri].setdefault("seed_report", {})
                self.seed_metadata["seeds"][uri]["seed_report"]= seed_report_metadata[uri]

            self.seed_metadata["timestamps"] = {}

            self.seed_metadata["timestamps"]["seed_metadata_timestamp"] = timestamp

            self.seed_metadata["timestamps"]["seed_report_timestamp"] = seed_report_timestamp

            self.seed_metadata_loaded = True

    def get_collection_name(self):
        """Getter for the collection name, as scraped."""

        self.load_collection_metadata()

        name = self.metadata["main"]["name"]

        return name

    def get_collection_uri(self):
        """Getter for the collection URI, as constructed."""

        self.load_collection_metadata()
        #https%3A%2F%2Fwebarchive.nla.gov.au%2Fcollection%2F15003

        uri = self.metadata["main"]["collection_uri"]

        return uri

    def get_collectedby(self):
        """Getter for the collecting organization's name, as scraped."""

        self.load_collection_metadata()
        #List of agencies
        collectedby = self.metadata["main"]["institution_name"]

        return collectedby

    def get_collectedby_uri(self):
        """Getter for the collecting organization's URI, as constructed."""

        self.load_collection_metadata()
        #List of agencies
        uri = self.metadata["main"]["institution_uri"]

        return uri

    def get_description(self):
        """Getter for the collection description, as scraped."""

        self.load_collection_metadata()
        #No description
        description = self.metadata["main"]["description"]

        return description

    def get_subject(self):
        """Getter for the collection's topics, as scraped."""
        
        self.load_collection_metadata()

        subjects = self.metadata["main"]["subject"]

        return subjects

    def get_archived_since(self):
        """Getter for the collection's archived since field, as scraped."""

        self.load_collection_metadata()

        archived_since = self.metadata["main"]["archived_since"]

        return archived_since


    def get_archived_until(self):
        """Getter for the collection's archived since field, as scraped."""

        self.load_collection_metadata()

        archived_since = self.metadata["main"]["archived_until"]

        return archived_since
        
    def does_exist(self):
        """Returns `True` if the collection actually exists and requests for
        its data did not result in 404s or soft-404s."""

        self.load_collection_metadata()

        exists = self.metadata["main"]["exists"]

        #self.logger.debug("exists is set to {}".format(exists))

        return exists


    # def get_optional_metadata(self, key):
    #     """Given optional metadata field `key`, returns value as scraped."""

    #     self.load_collection_metadata()

    #     value = self.metadata["optional"][key]

    #     return value

    # def list_optional_metadata_fields(self):
    #     """Lists the optional metadata fields, as scraped."""

    #     self.load_collection_metadata()

    #     keylist = self.metadata["optional"].keys()

    #     return keylist

    # def is_private(self):
    #     """Returns `True` if the collection is public, otherwise `False`."""

    #     self.load_collection_metadata()

    #     if self.does_exist():

    #         if self.metadata["main"]["public"] == "private":
    #             return True
    #         elif self.metadata["main"]["public"] == "public":
    #             return False
    #         else:
    #             raise ArchiveItCollectionException("Could not determine private/public status")

    #     else:
    #         return False
    # def list_seed_uris(self):
    #     """Lists the seed URIs of an Archive-It collection."""

    #     self.load_collection_metadata()
    #     self.load_seed_metadata()

    #     return list(self.seed_metadata["seeds"].keys())

    # def get_seed_metadata(self, uri):
    #     """Returns a `dict` of seed metadata associated with the memento 
    #     at `uri`."""

    #     d = self.seed_metadata["seeds"][uri] 

    #     return d

    # def return_collection_metadata_dict(self):
    #     """Returns a `dict` of collection metadata."""

    #     self.load_collection_metadata()

    #     metadata = {
    #         "id": self.collection_id
    #     }    

    #     metadata["exists"] = self.does_exist()
    #     metadata["metadata_timestamp"] = \
    #         datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #     if metadata["exists"]:

    #         metadata["name"] = self.get_collection_name()
    #         metadata["uri"] = self.get_collection_uri()
    #         metadata["collected_by"] = self.get_collectedby()
    #         metadata["collected_by_uri"] = self.get_collectedby_uri()
    #         metadata["description"] = self.get_description()
    #         metadata["subject"] = self.get_subject()
    #         metadata["archived_since"] = self.get_archived_since()
    #         metadata["private"] = self.is_private()
    #         metadata["optional"] = {}

    #         for key in self.list_optional_metadata_fields():
    #             metadata["optional"][key] = self.get_optional_metadata(key)

    #     return metadata

    # def return_seed_metadata_dict(self):
    #     """Returns all seed metadata of all mementos as a `dict`."""

    #     self.load_seed_metadata()

    #     metadata = {
    #         "id": self.collection_id
    #     }

    #     metadata["seed_metadata"] = self.seed_metadata

    #     if len(metadata["seed_metadata"]) > 0:

    #         metadata["seed_metadata"]["timestamps"]["seed_metadata_timestamp"] = \
    #                 self.seed_metadata["timestamps"]["seed_metadata_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
    #         metadata["seed_metadata"]["timestamps"]["seed_report_timestamp"] = \
    #                 self.seed_metadata["timestamps"]["seed_report_timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    #     return metadata


    # def return_all_metadata_dict(self):
    #     """Returns all metadata of the collection as a `dict`."""

    #     self.load_collection_metadata()
    #     self.load_seed_metadata()

    #     collection_metadata = self.return_collection_metadata_dict()
        
    #     collection_metadata["seed_metadata"] = self.seed_metadata

    #     if len(collection_metadata["seed_metadata"]) > 0:

    #         collection_metadata["seed_metadata"]["timestamps"]["seed_metadata_timestamp"] = \
    #             self.seed_metadata["timestamps"]["seed_metadata_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
    #         collection_metadata["seed_metadata"]["timestamps"]["seed_report_timestamp"] = \
    #             self.seed_metadata["timestamps"]["seed_report_timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    #     return collection_metadata
        
    # def save_all_metadata_to_file(self, filename):
    #     """Saves all metadata to `filename` in JSON format."""

    #     collection_metadata = self.return_all_metadata_dict()

    #     with open(filename, 'w') as metadata_file:
    #         json.dump(collection_metadata, metadata_file, indent=4)

