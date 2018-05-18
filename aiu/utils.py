# -*- coding: utf-8 -*-

"""
aiu.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains functions used to download mementos and TimeMaps and 
process them.

Note: There be dragons here. This code was originally written for a different 
project. I'm sure it can be improved.
"""

import os
import logging
import multiprocessing
import csv
import json
import hashlib
import random

from requests_futures.sessions import FuturesSession
from requests.exceptions import ConnectionError, TooManyRedirects

from .archive_information import generate_raw_urim
from .timemap import convert_LinkTimeMap_to_dict
from .version import user_agent_string

logger = logging.getLogger(__name__)
cpu_count = multiprocessing.cpu_count()

def get_head_responses(session, uris):
    """This function creates a futures object for each URI-M in `uris,
    using an existing `session` object from requests-futures. Only HEAD
    requests are performed.
    """ 

    futures = {}

    for uri in uris:

        logger.debug("issuing HEAD on uri {}".format(uri))

        futures[uri] = session.head(uri, 
            headers={'user-agent': user_agent_string},
            allow_redirects=True)

    return futures

def get_uri_responses(session, raw_uris):
    """This function creates a futures object for each URI-M in `raw_uris`,
    using an existing `session` object from requests-futures. Only GET
    requests are performed.
    """

    futures = {}

    for uri in raw_uris:

        logger.debug("issuing GET on uri {}".format(uri))

        futures[uri] = session.get(uri, 
            headers={'user-agent': user_agent_string},
            stream=True)

    return futures

def generate_archiveit_urits(cid, seed_uris):
    """This function generates TimeMap URIs (URI-Ts) for a list of `seed_uris`
    from an Archive-It colleciton specified by `cid`.
    """

    urit_list = []

    for urir in seed_uris:
        urit = "http://wayback.archive-it.org/{}/timemap/link/{}".format(
            cid, urir
        )

        urit_list.append(urit)  

    return urit_list

def discover_raw_urims(urimlist, futures=None):
    """This function checks that the URI-Ms in `urimlist` are valid mementos,
    following all redirects and checking for a Memento-Datetime header.
    """

    raw_urimdata = {}
    errordata = {}

    if futures == None:
        with FuturesSession(max_workers=cpu_count) as session:
            futures = get_head_responses(session, urimlist)

    working_uri_list = list(futures.keys())

    completed_urims = []

    # for urim in list_generator(working_uri_list):
    while len(completed_urims) < len(list(working_uri_list)):

        urim = random.choice(
            list(set(working_uri_list) - set(completed_urims))
        )

        logger.debug("checking if URI-M {} is done downloading".format(urim))

        if futures[urim].done():

            logger.debug("searching for raw version of URI-M {}".format(urim))

            try:

                response = futures[urim].result()

                if "memento-datetime" in response.headers:

                    if len(response.history) == 0:
                        raw_urimdata[urim] = generate_raw_urim(urim)
                    else:
                        raw_urimdata[urim] = generate_raw_urim(response.url)

                    logger.debug("added raw URI-M {} associated with URI-M {}"
                        " to the list to be downloaded".format(raw_urimdata[urim], urim))

                else:

                    warn_msg = "No Memento-Datetime in Response Headers for " \
                        "URI-M {}".format(urim)

                    logger.warning(warn_msg)
                    errordata[urim] = warn_msg

            except ConnectionError as e:
                logger.warning("While acquiring memento at {} there was an error of {}, "
                    "this event is being recorded".format(urim, repr(e)))
                errordata[urim] = repr(e)

            except TooManyRedirects as e:
                logger.warning("While acquiring memento at {} there was an error of {},"
                    "this event is being recorded".format(urim, repr(e)))
                errordata[urim] = repr(e)

            finally:
                logger.debug("Removing URI-M {} from the processing list".format(urim))
                completed_urims.append(urim)

    return raw_urimdata, errordata

def list_generator(input_list):
    """This function generates the next item in a list. It is useful for lists
    that have their items deleted while one is iterating through them.
    """

    logger.debug("list generator called")

    while len(input_list) > 0:
        for item in input_list:
            logger.debug("list now has {} items".format(len(input_list)))
            logger.debug("yielding {}".format(item))
            yield item

def process_timemaps_for_mementos(urit_list, working_directory):
    """This function acquires a list of mementos from a list of TimeMaps URIs.
    The TimeMaps are stored in `working_directory`.
    """

    timemap_data = {}

    output_directory = "{}/capture/timemaps".format(working_directory)

    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    with FuturesSession(max_workers=cpu_count) as session:
        futures = get_uri_responses(session, urit_list)

    working_uri_list = list(futures.keys())

    with open("{}/manifest.tsv".format(output_directory), 'w') as manifestout:

        with open("{}/errors.jsonl".format(output_directory), 'w') as errorsout:

            fieldnames = [ "URI-T", "Filename"]

            manifestwriter = csv.DictWriter(manifestout, fieldnames, delimiter='\t')
            manifestwriter.writeheader()

            for urit in list_generator(working_uri_list):

                logger.debug("checking if URI-T {} is done downloading".format(urit))

                if futures[urit].done():

                    logger.debug("URI-T {} is done, extracting content".format(urit))

                    try:
                        response = futures[urit].result()

                        http_status = response.status_code

                        if http_status == 200:

                            timemap_content = response.text

                            logger.info("adding TimeMap content for URI-T {}".format(
                                urit))

                            uritfilename = hashlib.sha256(urit.encode('utf8')).hexdigest()

                            with open("{}/{}".format(
                                output_directory, uritfilename), 'w') as tmout:
                                tmout.write(timemap_content)

                            timemap_data[urit] = convert_LinkTimeMap_to_dict(
                                timemap_content, skipErrors=True)

                            manifestwriter.writerow({
                                'URI-T': urit,
                                'Filename': uritfilename
                            })

                        else:
                            errorsout.write("{}\n".format(json.dumps(
                                {
                                    "URI-T": urit,
                                    "status": http_status,
                                    "headers": dict(response.headers)
                                }
                            )))

                        # TODO: else store connection errors
                        working_uri_list.remove(urit)
                    
                    except ConnectionError as e:

                        logger.warning("There was a connection error while attempting "
                            "to download URI-T {}".format(urit))

                        errorsout.write(json.dumps(
                            {
                                "URI-T": urit,
                                "error": repr(e)
                            }
                        ))

                        # TODO: store connection errors in CollectionModel
                        working_uri_list.remove(urit)

                    except TooManyRedirects as e:

                        logger.warning("There were too many redirects while attempting "
                            "to download URI-T {}".format(urit))

                        errorsout.write(json.dumps(
                            {
                                "URI-T": urit,
                                "error": repr(e)
                            }
                        ))

                        # TODO: store connection errors in CollectionModel
                        working_uri_list.remove(urit)

    return timemap_data

