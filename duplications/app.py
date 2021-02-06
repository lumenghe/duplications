""" this file to find duplication movies """
import argparse
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DuplicationsFinder:
    """Class to find duplication movies"""

    LEFT_THRESHOLD = 0.95
    RIGHT_THRESHOLD = 1.05

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._id2data = {}
        self._year2ids = defaultdict(set)
        self._genre2ids = defaultdict(set)

    def read_file(self, filepath):
        pass

    def process(self, output):
        """process to find duplications and save in output file
        :param output: output file path
        :return: None
        """
        years = sorted(self._year2ids.keys())
        genres = sorted(self._genre2ids.keys())

        matchings = self.process_per_year(years, genres)

        # save duplications per year
        self.save_duplicates(matchings, output)

    def process_per_year(self, years, genres):
        ...

    def process_per_genre(self, sel_years, genres, matchings):
        ...
