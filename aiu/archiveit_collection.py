# -*- coding: utf-8 -*-

"""
aiu.archiveit_collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module acquires data about an Archvie-It collection both from its results
pages and its CSV seed report.

Note: There be dragons here. This code was originally written for a different 
project. I'm sure it can be improved.
"""

# TODO: allow one to specify a session object from requests

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

collection_uri_prefix = "https://archive-it.org/collections"

class ArchiveItCollectionException(Exception):
    """An exception class to be used by the functions in this file so that the
    source of error can be detected.
    """
    pass

def scrape_main_collection_data(soup):
    """Scrapes general collection metadata the Archive-It collection
    results page using the BeautfulSoup object `soup`.
    """

    data = {}

    metadata_tags = soup.find_all("div", "entity-meta")

    try:
        data["name"] = metadata_tags[0].find_all("h1")[0].get_text().strip()
        data["exists"] = True
    except IndexError:

        try:

            if "Not Found" in metadata_tags[0].find_all("h2")[0].get_text().strip():
                data["exists"] = False
                return data
            else:
                raise IndexError("Could not find 'Not Found' string using screen scraping")

        except IndexError as e:
            logger.error("Failed to find collection name using screen scraping")
            logger.error("Failed to determine if collection does not exist using screen scraping")
            logger.error(metadata_tags)
            raise e

    try:
        data["collection_uri"] = metadata_tags[0].find_all("h1")[0].find_all("a")[0]["href"]
    except IndexError as e:
        logger.error("Failed to find collection URI using screen scraping")
        logger.error(metadata_tags)
        raise e

    try:
        data["institution_name"] = \
            metadata_tags[0].find_all("p", "collectedBy")[0].get_text().strip().replace("Collected by:", "").strip()
    except IndexError as e:
        logger.error("Failed to find institution name using screen scraping")
        logger.error(metadata_tags)
        raise e

    try:
        data["institution_uri"] = metadata_tags[0].find_all("p", "collectedBy")[0].find_all("a")[0]['href']
    except IndexError as e:
        logger.error("Failed to find institution URI using screen scraping")
        logger.error(metadata_tags)
        raise e

    try:
        data["description"] = \
            metadata_tags[0].find_all("p", "seamTextPara")[0].get_text().strip().replace('\n', '<br />')
    except IndexError:
        logger.warning("Failed to find description using screen scraping, "
            "setting to No description...")
        data["description"] = "No description."

    search_results = soup.find_all("div", {"id": "all-search-results"})

    try:
        public_stmt = search_results[0].find_all("h2")[0].get_text().strip()

        if "There is no public content available for this Collection yet. Please check back soon!" in public_stmt:
            data["public"] = "private"
        else:
            data["public"] = "public"

    except IndexError:
        data["public"] = "unknown" 

    data["archived_since"] = "unknown"

    subjects = []

    for item in metadata_tags[0].find_all("p"):

        bolds = item.find_all('b')

        if len(bolds) > 0:

            for bold in bolds:

                if "Subject" in bold.get_text():
                    subjects = [i.strip(',').strip() for i in item.text.replace('Subject:', '').replace('\xa0', '').replace('\t', '').strip().split('\n')]

                if "Archived since" in bold.get_text():
                    archived_since = [i.strip(',').strip() for i in item.text.replace('Archived since:', '').replace('\xa0', '').replace('\t', '').strip().split('\n')][0]

    data["subject"] = subjects
    data["archived_since"] = archived_since

    return data

def scrape_optional_collection_data(soup):
    """Scrapes optional collection metadata the Archive-It collection
    results page using the BeautfulSoup object `soup`.
    """

    data = {}

    metadata_tags = soup.find_all("div", "entity-meta")

    if len(metadata_tags) > 0:

        moreMetadata = metadata_tags[0].find_all("div", "moreMetadata")

        if len(moreMetadata) > 0:

            for item in moreMetadata[0].find_all("p"):
                key = item.find_all("b")[0].text.replace('\xa0', '').strip().strip(':')
                values = [i.strip(',').strip() for i in item.text.replace("{}:".format(key), '').replace('\xa0', '').replace('\t', '').strip().split('\n')]
                key = key.lower()
                data[key] = values

    return data

def scrape_seed_metadata(soup):
    """Scrapes the seed metadata from an Archive-It results page stored in the
    BeautifulSoup object `soup`.
    """

    data = []

    for item in soup.find_all("div", "result-item"):

        itemdict = {}

        for entry in item.find_all("h3", "url"):
    
            if 'URL:' in entry.text:
                url = entry.text.replace("URL:", "").strip()
                itemdict["uri"] = url

            if 'Title:' in entry.text:
                title = entry.text.replace("Title:", "").strip()
                itemdict["title"] = title

        for entry in item.find_all("p"):
            if len(entry.find_all("b")) > 0:
                key = entry.find_all("b")[0].text.replace('\xa0', '').strip().rstrip(':')
                #value = entry.find_all("a")[0].text.strip()
                values = [i.strip(',').strip() for i in entry.text.replace("{}:".format(key), '').replace('\xa0', '').replace('\t', '').strip().split('\n')]
                itemdict[key.lower()] = values

        data.append(itemdict)

    return data

def scrape_page_count(soup):
    """Scrapes the page count from an Archive-It results page stored in the
    BeautifulSoup object `soup`.
    """

    try:
        pagestring = soup.find_all("div", "paginator")[0].text
        page_count = pagestring.split("of")[1].strip().split()[0]
        page_count = page_count.replace(',', '')
    except IndexError:
        page_count = None

    return page_count

def scrape_page_number(soup):
    """Scrapes the page number from an Archive-It results page stored in the
    BeautifulSoup object `soup`.
    """

    try:
        pagestring = soup.find_all("div", "paginator")[0].text
        print("pagestring: {}".format(pagestring))
        page_number = pagestring.split("of")[0].strip().split()[1]
        page_number = page_number.replace(',', '')
    except IndexError:
        page_number = None

    return page_number

def scrape_result_count(soup):
    """Scrapes the result count from an Archive-It results page stored in the
    BeautifulSoup object `soup`.
    """

    try:
        pagestring = soup.find_all("div", "paginator")[0].text
        result_count = pagestring[pagestring.find('(') + 1:].replace(' Total Results', '').rstrip(')')
        result_count = pagestring[pagestring.find('(') + 1:pagestring.find(' Total Results')]
        result_count = result_count.replace(',', '')
    except IndexError:
        result_count = None

    return result_count


def scrape_next_page_number(soup):
    """Scrapes the Next Page URI from an Archive-It results page stored in
    the BeautifulSoup object `soup`.
    """

    nextpage = None

    nextpagematch = soup.find_all('a', {'id': 'pageNext'})

    if len(nextpagematch) == 2:
        nextpage_uri = nextpagematch[0]['href'] 
        nextpage = nextpage_uri[nextpage_uri.find('page='):][:nextpage_uri.find('&') - 1].replace("page=", "") 

    return nextpage

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

class ArchiveItCollection:
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

        self.collection_uri = "{}/{}".format(collection_uri_prefix, collection_id)
        self.firstpage_response = self.session.get(self.collection_uri)        

        self.logger = logger or logging.getLogger(__name__)

    def load_collection_metadata(self):
        """Loads collection metadata from an existing directory, if possible.
        If the existing directory does not exist, it will then download the
        collection and process its metadata.
        """

        if not self.metadata_loaded:

            soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')

            self.metadata["main"] = scrape_main_collection_data(soup)
            self.metadata["optional"] = scrape_optional_collection_data(soup)

            self.metadata_loaded = True

    def load_seed_metadata(self):
        """Loads the seed metadata previously downloaded if possible, otherwise
        acquires all collection results pages and parses them for seed metadata.

        This function is separate to limit the number of requests. It should only
        be called if seed metadata is needed.
        """

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

            soup = BeautifulSoup(self.firstpage_response.text, 'html5lib')

            seed_metadata_list.extend( scrape_seed_metadata(soup) )

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

        uri = "https://archive-it.org{}".format(self.metadata["main"]["collection_uri"])

        return uri

    def get_collectedby_uri(self):
        """Getter for the collecting organization's URI, as constructed."""

        self.load_collection_metadata()

        uri = "https://archive-it.org{}".format(self.metadata["main"]["institution_uri"])

        return uri

    def get_description(self):
        """Getter for the collection description, as scraped."""

        self.load_collection_metadata()

        description = self.metadata["main"]["description"]

        return description

    def get_collectedby(self):
        """Getter for the collecting organization's name, as scraped."""

        self.load_collection_metadata()

        collectedby = self.metadata["main"]["institution_name"]

        return collectedby

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

    def get_optional_metadata(self, key):
        """Given optional metadata field `key`, returns value as scraped."""

        self.load_collection_metadata()

        value = self.metadata["optional"][key]

        return value

    def list_optional_metadata_fields(self):
        """Lists the optional metadata fields, as scraped."""

        self.load_collection_metadata()

        keylist = self.metadata["optional"].keys()

        return keylist

    def is_private(self):
        """Returns `True` if the collection is public, otherwise `False`."""

        self.load_collection_metadata()

        if self.does_exist():

            if self.metadata["main"]["public"] == "private":
                return True
            elif self.metadata["main"]["public"] == "public":
                return False
            else:
                raise ArchiveItCollectionException("Could not determine private/public status")

        else:
            return False

    def does_exist(self):
        """Returns `True` if the collection actually exists and requests for
        its data did not result in 404s or soft-404s."""

        self.load_collection_metadata()

        exists = self.metadata["main"]["exists"]

        #self.logger.debug("exists is set to {}".format(exists))

        return exists

    def list_seed_uris(self):
        """Lists the seed URIs of an Archive-It collection."""

        self.load_collection_metadata()
        self.load_seed_metadata()

        return list(self.seed_metadata["seeds"].keys())

    def get_seed_metadata(self, uri):
        """Returns a `dict` of seed metadata associated with the memento 
        at `uri`."""

        d = self.seed_metadata["seeds"][uri] 

        return d

    def return_collection_metadata_dict(self):
        """Returns a `dict` of collection metadata."""

        self.load_collection_metadata()

        metadata = {
            "id": self.collection_id
        }    

        metadata["exists"] = self.does_exist()
        metadata["metadata_timestamp"] = \
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if metadata["exists"]:

            metadata["name"] = self.get_collection_name()
            metadata["uri"] = self.get_collection_uri()
            metadata["collected_by"] = self.get_collectedby()
            metadata["collected_by_uri"] = self.get_collectedby_uri()
            metadata["description"] = self.get_description()
            metadata["subject"] = self.get_subject()
            metadata["archived_since"] = self.get_archived_since()
            metadata["private"] = self.is_private()
            metadata["optional"] = {}

            for key in self.list_optional_metadata_fields():
                metadata["optional"][key] = self.get_optional_metadata(key)

        return metadata

    def return_seed_metadata_dict(self):
        """Returns all seed metadata of all mementos as a `dict`."""

        self.load_seed_metadata()

        metadata = {
            "id": self.collection_id
        }

        metadata["seed_metadata"] = self.seed_metadata

        if len(metadata["seed_metadata"]) > 0:

            metadata["seed_metadata"]["timestamps"]["seed_metadata_timestamp"] = \
                    self.seed_metadata["timestamps"]["seed_metadata_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
            metadata["seed_metadata"]["timestamps"]["seed_report_timestamp"] = \
                    self.seed_metadata["timestamps"]["seed_report_timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return metadata


    def return_all_metadata_dict(self):
        """Returns all metadata of the collection as a `dict`."""

        self.load_collection_metadata()
        self.load_seed_metadata()

        collection_metadata = self.return_collection_metadata_dict()
        
        collection_metadata["seed_metadata"] = self.seed_metadata

        if len(collection_metadata["seed_metadata"]) > 0:

            collection_metadata["seed_metadata"]["timestamps"]["seed_metadata_timestamp"] = \
                self.seed_metadata["timestamps"]["seed_metadata_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
            collection_metadata["seed_metadata"]["timestamps"]["seed_report_timestamp"] = \
                self.seed_metadata["timestamps"]["seed_report_timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return collection_metadata
        
    def save_all_metadata_to_file(self, filename):
        """Saves all metadata to `filename` in JSON format."""

        collection_metadata = self.return_all_metadata_dict()

        with open(filename, 'w') as metadata_file:
            json.dump(collection_metadata, metadata_file, indent=4)

