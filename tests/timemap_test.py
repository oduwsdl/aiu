import unittest
import pprint
import datetime

from aiu import convert_LinkTimeMap_to_dict

pp = pprint.PrettyPrinter(indent=4)

class TestTimeMapParser(unittest.TestCase):

    def test_good_link_headers(self):

        lheader = '<http://ogp.me:80/>; rel="original", <https://web.archive.org/web/timemap/link/http://ogp.me:80/>; rel="timemap"; type="application/link-format", <https://web.archive.org/web/http://ogp.me:80/>; rel="timegate", <https://web.archive.org/web/20100802055126/http://ogp.me:80/>; rel="first memento"; datetime="Mon, 02 Aug 2010 05:51:26 GMT", <https://web.archive.org/web/20100802055126/http://ogp.me:80/>; rel="memento"; datetime="Mon, 02 Aug 2010 05:51:26 GMT", <https://web.archive.org/web/20101211091635/http://ogp.me/>; rel="next memento"; datetime="Sat, 11 Dec 2010 09:16:35 GMT", <https://web.archive.org/web/20210106030214/https://ogp.me/>; rel="last memento"; datetime="Wed, 06 Jan 2021 03:02:14 GMT"'

        actual_json_timemap = convert_LinkTimeMap_to_dict(lheader)

        expected_json_timemap = {   
            'mementos': {   'first': {   'datetime': datetime.datetime(2010, 8, 2, 5, 51, 26),
                                        'uri': 'https://web.archive.org/web/20100802055126/http://ogp.me:80/'},
                            'last': {   'datetime': datetime.datetime(2021, 1, 6, 3, 2, 14),
                                        'uri': 'https://web.archive.org/web/20210106030214/https://ogp.me/'},
                            'list': [   {   'datetime': datetime.datetime(2010, 8, 2, 5, 51, 26),
                                            'uri': 'https://web.archive.org/web/20100802055126/http://ogp.me:80/'},
                                        {   'datetime': datetime.datetime(2010, 8, 2, 5, 51, 26),
                                            'uri': 'https://web.archive.org/web/20100802055126/http://ogp.me:80/'},
                                        {   'datetime': datetime.datetime(2010, 12, 11, 9, 16, 35),
                                            'uri': 'https://web.archive.org/web/20101211091635/http://ogp.me/'},
                                        {   'datetime': datetime.datetime(2021, 1, 6, 3, 2, 14),
                                            'uri': 'https://web.archive.org/web/20210106030214/https://ogp.me/'}]},
            'original_uri': 'http://ogp.me:80/',
            'timegate_uri': 'https://web.archive.org/web/http://ogp.me:80/',
            'timemap_uri': {
                "link_format": "https://web.archive.org/web/timemap/link/http://ogp.me:80/"
            }
        }

        # pp.pprint(actual_json_timemap)

        self.assertEqual( actual_json_timemap, expected_json_timemap )

    def test_example_multiple_urits(self):

        lheader = '<http://ogp.me>; rel="original", <https://perma.cc/timegate/http://ogp.me>; rel="timegate", <https://perma.cc/timemap/link/http://ogp.me>; rel="timemap"; type="application/link-format", <https://perma.cc/timemap/json/http://ogp.me>; rel="timemap"; type="application/json", <https://perma.cc/timemap/html/http://ogp.me>; rel="timemap"; type="text/html", <https://perma.cc/7YXW-UFQ3>; rel="memento"; datetime="Sun, 04 Oct 2015 23:18:13 GMT"'

        actual_json_timemap = convert_LinkTimeMap_to_dict(lheader, debug=False)

        # print("output in test")
        # pp.pprint(actual_json_timemap)

        expected_json_timemap = {   
            'mementos': {   'list': [   {   'datetime': datetime.datetime(2015, 10, 4, 23, 18, 13),
                                    'uri': 'https://perma.cc/7YXW-UFQ3'}]},
            'original_uri': 'http://ogp.me',
            'timegate_uri': 'https://perma.cc/timegate/http://ogp.me',
            'timemap_uri': {
                'json_format': 'https://perma.cc/timemap/json/http://ogp.me',
                'link_format': 'https://perma.cc/timemap/link/http://ogp.me'}
        }

        # Note that the HTML timemap is not listed because http://mementoweb.org/guide/timemap-json/ does not specify it
        self.assertEqual( actual_json_timemap, expected_json_timemap )

    def test_7089_fig28(self):

        timemap = """    <http://a.example.org>;rel="original",
    <http://arxiv.example.net/timemap/http://a.example.org>
      ; rel="self";type="application/link-format"
      ; from="Tue, 20 Jun 2000 18:02:59 GMT"
      ; until="Wed, 09 Apr 2008 20:30:51 GMT",
    <http://arxiv.example.net/timegate/http://a.example.org>
      ; rel="timegate",
    <http://arxiv.example.net/web/20000620180259/http://a.example.org>
      ; rel="first memento";datetime="Tue, 20 Jun 2000 18:02:59 GMT"
      ; license="http://creativecommons.org/publicdomain/zero/1.0/",
    <http://arxiv.example.net/web/20091027204954/http://a.example.org>
       ; rel="last memento";datetime="Tue, 27 Oct 2009 20:49:54 GMT"
       ; license="http://creativecommons.org/publicdomain/zero/1.0/",
    <http://arxiv.example.net/web/20000621011731/http://a.example.org>
      ; rel="memento";datetime="Wed, 21 Jun 2000 01:17:31 GMT"
      ; license="http://creativecommons.org/publicdomain/zero/1.0/",
    <http://arxiv.example.net/web/20000621044156/http://a.example.org>
      ; rel="memento";datetime="Wed, 21 Jun 2000 04:41:56 GMT"
      ; license="http://creativecommons.org/publicdomain/zero/1.0/"
      """

        actual_json_timemap = convert_LinkTimeMap_to_dict(timemap, debug=False)

        # print("output in test")
        # pp.pprint(actual_json_timemap)

        expected_json_timemap = {   
            'mementos': {   
                'first': {   'datetime': datetime.datetime(2000, 6, 20, 18, 2, 59),
                                 'uri': 'http://arxiv.example.net/web/20000620180259/http://a.example.org'},
                    'last': {   'datetime': datetime.datetime(2009, 10, 27, 20, 49, 54),
                                'uri': 'http://arxiv.example.net/web/20091027204954/http://a.example.org'},
                    'list': [   {   'datetime': datetime.datetime(2000, 6, 20, 18, 2, 59),
                                    'uri': 'http://arxiv.example.net/web/20000620180259/http://a.example.org'},
                                {   'datetime': datetime.datetime(2009, 10, 27, 20, 49, 54),
                                    'uri': 'http://arxiv.example.net/web/20091027204954/http://a.example.org'},
                                {   'datetime': datetime.datetime(2000, 6, 21, 1, 17, 31),
                                    'uri': 'http://arxiv.example.net/web/20000621011731/http://a.example.org'},
                                {   'datetime': datetime.datetime(2000, 6, 21, 4, 41, 56),
                                    'uri': 'http://arxiv.example.net/web/20000621044156/http://a.example.org'}]},
            'original_uri': 'http://a.example.org',
            'timegate_uri': 'http://arxiv.example.net/timegate/http://a.example.org',
            'timemap_uri': {   'link_format': 'http://arxiv.example.net/timemap/http://a.example.org'}
        }

        self.assertEqual( actual_json_timemap, expected_json_timemap )

    # def test_example_multiple_urits_missing_quotes(self):

    #     lheader = '<http://ogp.me>; rel=original, <https://perma.cc/timegate/http://ogp.me>; rel=timegate, <https://perma.cc/timemap/link/http://ogp.me>; rel=timemap; type=application/link-format, <https://perma.cc/timemap/json/http://ogp.me>; rel=timemap; type=application/json, <https://perma.cc/timemap/html/http://ogp.me>; rel=timemap; type=text/html, <https://perma.cc/7YXW-UFQ3>; rel=memento; datetime="Sun, 04 Oct 2015 23:18:13 GMT"'

    #     actual_json_timemap = convert_LinkTimeMap_to_dict(lheader, debug=False)

        # print("output in test")
        # pp.pprint(actual_json_timemap)
