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
        """process per year to find duplications
        :param years: list of years.
        :param genres: list of genres.
        :return: matchings result
        """
        matchings = defaultdict(set)
        # Process by year, year+1
        for prev_year, year in zip(years[:-1], years[1:]):
            sel_years = [prev_year, year] if prev_year == year - 1 else [year]
            matchings = self.process_per_genre(sel_years, genres, matchings)

        return matchings

    def process_per_genre(self, sel_years, genres, matchings):
        """process per process_per_genre to find duplications
        :param sel_years: group by years which could have duplication movies
        :param genres: list of genres.
        :param matchings: matchings saved
        :return: matchings result
        """
        year_ids = set.union(
            *[self._year2ids[year] for year in sel_years]
        )  # ids for selected years
        matches = 0
        candidates = 0
        for genre in genres:
            genre_ids = self._genre2ids[genre]  # ids for selected genre
            sel_ids = list(
                year_ids.intersection(genre_ids.union(self._genre2ids["\\N"]))
            )

            for i, id_i in enumerate(sel_ids):
                data_i = self._id2data[id_i]
                for _, id_j in enumerate(sel_ids[i + 1 :]):
                    data_j = self._id2data[id_j]
                    candidates += 1
                    if (
                            data_i["min_length"]
                            < data_j["length"]
                            < data_i["max_length"]
                            and data_j["min_length"]
                            < data_i["length"]
                            < data_j["max_length"]
                    ):
                        name_matches = self.check_names(
                            data_i["directors"], data_j["directors"]
                        ) + self.check_names(
                            data_i["actors"], data_j["actors"]
                        )
                        if name_matches >= 3:
                            matchings[id_i].add(id_j)
                            matches += 1

        logger.info(
            "Year %s. Number of matchings: %d / %d (total: %d)",
            sel_years,
            matches,
            candidates,
            sum(len(v) for v in matchings.values()),
        )

        return matchings

    @staticmethod
    def check_names(names, others):
        """check_names
        :param name: 1st name to check
        :param other: 2nd name to check
        :return: int
            0 if both \\N or no subset,
            1 if one is \\N,
            2 if both not \\N and one subset of the other
        """
        if not names and not others:
            return 0

        if not names or not others:
            return 1

        if names.issubset(others) or others.issubset(names):
            return 2

        return 0

    @staticmethod
    def save_duplicates(matchings, save_file):
        """save duplicates
        :param matchings: matchings results
        :param save file: output file
        :return: None
        """
        with open(save_file, "w") as output:
            for ref_id, movies in matchings.items():
                lines = [ref_id + "\t" + mov_id + "\n" for mov_id in movies]
                output.writelines(lines)
        output.close()
