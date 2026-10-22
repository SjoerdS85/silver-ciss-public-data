import unittest

from src.common import ContractError
from src.public_readback import extract_tag


class PublicReadbackTests(unittest.TestCase):
    def test_extract_tag(self):
        url = (
            "https://github.com/SjoerdS85/silver-ciss-public-data/releases/download/"
            "ciss-20261020-01a9f9279038/ciss_snapshot.csv"
        )
        self.assertEqual(extract_tag(url), "ciss-20261020-01a9f9279038")

    def test_reject_wrong_repository(self):
        with self.assertRaises(ContractError):
            extract_tag("https://github.com/other/repo/releases/download/t/file.csv")

    def test_reject_non_release_url(self):
        with self.assertRaises(ContractError):
            extract_tag("https://example.com/file.csv")


if __name__ == "__main__":
    unittest.main()
