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
        """read file by filepath
        :param filepath: csv / tsv file path
        :return: None
        """
        with open(filepath, "r") as content:
            for i, line in enumerate(content):
                if i == 0:
                    continue  # skip header

                l = line.strip().split("\t")
                _id = l[0]

                _year = int(l[1])
                _length = int(l[2])
                _genres = l[3]
                _directors = (
                    set(l[4].strip().split(","))
                    if l[4].strip() != "\\N"
                    else set()
                )
                _actors = (
                    set(l[5].strip().split(","))
                    if l[5].strip() != "\\N"
                    else set()
                )
                self._id2data[_id] = dict(
                    length=_length,
                    directors=_directors,
                    actors=_actors,
                    min_length=self.LEFT_THRESHOLD * _length,
                    max_length=self.RIGHT_THRESHOLD * _length,
                )
                self._year2ids[_year].add(_id)
                for _genre in _genres.split(","):
                    self._genre2ids[_genre].add(_id)

                print(f"\rReading {i}", end="")

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
