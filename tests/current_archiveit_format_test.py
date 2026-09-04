import unittest

from bs4 import BeautifulSoup

from aiu.archiveit_collection import (
    ArchiveItCollection,
    scrape_main_collection_data,
    scrape_next_page_number,
    scrape_page_count,
    scrape_page_number,
    scrape_result_count,
)


CURRENT_COLLECTION_PAGE = """
<main>
  <div class="entity-header">
    <div class="entity-info">
      <h1>2013 Boston Marathon Bombing</h1>
      <div class="result-field"><span class="field-label">Collected by:</span>
        <a href="/organizations/89">Internet Archive Global Events</a>
      </div>
      <div class="result-field"><span class="field-label">Archived since:</span>
        Apr, 2013
      </div>
      <div class="result-field"><span class="field-label">Description:</span>
        A collection description.
      </div>
      <div class="result-field"><span class="field-label">Subject:</span>
        <a href="/collections/3649?fc=meta_Subject%3AspontaneousEvents">Spontaneous Events</a>
      </div>
    </div>
  </div>
  <div class="result-item">
    <h2><a href="https://wayback.archive-it.org/3649/*/https://example.org/">https://example.org/</a></h2>
    <div class="result-field"><span class="field-label">Type:</span>
      <a href="/collections/3649?fc=meta_Type%3ANews+Article">News Article</a>
    </div>
  </div>
  <div class="pagination">
    <span>Page 1 of 1 (1 total results)</span>
  </div>
</main>
"""


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeSession:
    seed_report = """active,publicly_visible,seed_type,url\nTrue,True,normal,https://example.org/\n"""

    def get(self, url, **kwargs):
        if "partner.archive-it.org/api/seed" in url:
            return FakeResponse(self.seed_report)
        return FakeResponse(CURRENT_COLLECTION_PAGE)


class TestCurrentArchiveItFormat(unittest.TestCase):
    def test_current_collection_metadata(self):
        metadata = scrape_main_collection_data(
            BeautifulSoup(CURRENT_COLLECTION_PAGE, "html.parser")
        )

        self.assertEqual(metadata["name"], "2013 Boston Marathon Bombing")
        self.assertEqual(metadata["collection_uri"], "/collections/3649")
        self.assertEqual(metadata["institution_name"], "Internet Archive Global Events")
        self.assertEqual(metadata["archived_since"], "Apr, 2013")
        self.assertEqual(metadata["subject"], ["Spontaneous Events"])
        self.assertEqual(metadata["public"], "public")

    def test_current_pagination(self):
        soup = BeautifulSoup(CURRENT_COLLECTION_PAGE, "html.parser")
        self.assertEqual(scrape_page_number(soup), "1")
        self.assertEqual(scrape_page_count(soup), "1")
        self.assertEqual(scrape_result_count(soup), "1")
        self.assertIsNone(scrape_next_page_number(soup))

    def test_current_seed_report_columns(self):
        collection = ArchiveItCollection(3649, session=FakeSession())

        self.assertEqual(collection.list_seed_uris(), ["https://example.org/"])
        self.assertEqual(
            collection.get_seed_metadata("https://example.org/")["seed_report"],
            {
                "group": "",
                "status": "True",
                "frequency": "",
                "type": "normal",
                "access": "True",
            },
        )


if __name__ == "__main__":
    unittest.main()
