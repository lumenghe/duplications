""" this file to find duplication movies """
import argparse
import logging
from collections import defaultdict

import pandas as pd

logger = logging.getLogger(__name__)


class DuplicationsFinder:
    """Class to find duplication movies"""

    LEFT_THRESHOLD = 1.95 / 2.05
    RIGHT_THRESHOLD = 2.05 / 1.95

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    @staticmethod
    def read_file(filepath):
        """read file by filepath
        :param filepath: csv / tsv file path
        :return: dataframe from file
        """
        df = pd.read_csv(filepath, sep="\t")
        return df

    def process(self, df, output):
        """process to find duplications and save in output file
        :param df: dataframe read from file
        :param output: output file path
        :return: None
        """
        df = df.sort_values(["year", "length"])

        # Get all unique years
        years = sorted(set(df["year"]))

        # Get all unique genre
        genres = set(df["genre"])
        genres = sorted(set.union(*(set(s.split(",")) for s in genres)))

        # Add one-hot encoding for all genres + \N
        for genre in genres:
            if genre != "\\N":
                col = df["genre"].str.contains(genre).values
            else:
                col = df["genre"] == "\\N"

            df.insert(0, genre, col)
            logger.info(f"added column {genre}.")
        # Add +/- %5 lengths
        df.insert(0, "min_length", self.LEFT_THRESHOLD * df["length"])
        df.insert(0, "max_length", self.RIGHT_THRESHOLD * df["length"])

        matchings = self.process_per_year(df, years, genres)

        final_matchings = self.post_process(matchings)

        # save duplications per year
        self.save_duplicates(final_matchings, output)

    def process_per_year(self, df, years, genres):
        """process per year to find duplications
        :param df: dataframe read from file
        :param years: list of years.
        :param genres: list of genres.
        :return: matchings result
        """
        matchings = defaultdict(set)
        # Process by year, year+1
        for prev_year, year in zip(years[:-1], years[1:]):
            sel_years = [prev_year, year] if prev_year == year - 1 else [year]
            data_block = df[df["year"].isin(sel_years)].sort_values(["length"])
            logger.info(f"year={year}, #movies={len(data_block)}")
            matchings = self.process_per_genre(genres, matchings, data_block)

        return matchings

    def process_per_genre(self, genres, matchings, data_block):
        """process per process_per_genre to find duplications
        :param genres: list of genres.
        :param matchings: matchings saved
        :param data_block: data block which hold duplications
        :return: matchings result
        """
        for genre in genres:
            genre_block = data_block[
                data_block[genre] | data_block["\\N"]
            ].sort_values(["length"])
            lengths = sorted(set(genre_block["length"]))
            # length buckets (process by bucket)
            len_buckets = [
                lengths[i : i + 20] for i in range(0, len(lengths), 10)
            ]

            logger.info(
                f"\tgenre={genre}, #movies (incl. unknown)={len(genre_block)}"
            )

            # Process by bucket
            for len_bkt in len_buckets:
                bkt_block = genre_block[genre_block["length"].isin(len_bkt)]
                for i, row_i in bkt_block.iterrows():
                    for _, row_j in bkt_block.iloc[i + 1 :].iterrows():
                        if (
                            self.check_naming(
                                row_i["directors"], row_j["directors"]
                            )
                            and self.check_naming(
                                row_i["actors"], row_j["actors"]
                            )
                            and row_i["min_length"]
                            < row_j["length"]
                            < row_i["max_length"]
                            and row_j["min_length"]
                            < row_i["length"]
                            < row_j["max_length"]
                        ):
                            matchings[row_i["id"]].add(row_j["id"])
        return matchings

    @staticmethod
    def post_process(matchings):
        """post process matchings as one movie id can only be used in one matching
        :param matchings: matchings results with movie id shown on more than one lines
        :return: new_ref2movies result, one movie id can only be used in one matching
        """
        movie2ref = (
            {}
        )  # id of duplicate -> ref_id (ref_id not included) i.e Movie2ref = {2:1, 3:1, 5:4}
        ref2movies = (
            {}
        )  # ref id to list of movies i.e Ref2movies = {1: {1,2,3}, 4:{4,5}}

        # ref id is defined as min id string
        logger.info("Post-processing matchings")
        for key, vals in matchings.items():
            ids = set([key]).union(vals)
            ref_id = min(ids)

            # merge
            merge_ref = set()
            for m_id in ids:
                merge_ref.add(movie2ref.get(m_id, ref_id))

            # new ref
            new_ref = min(merge_ref)
            merged_movies = set.union(
                *([ids] + [ref2movies.get(ref, set()) for ref in merge_ref])
            )

            # remove merged ref and replace with merged ref
            for ref in merge_ref:
                if ref in ref2movies:
                    del ref2movies[ref]

            ref2movies[new_ref] = merged_movies
            for m_id in merged_movies:
                movie2ref[m_id] = new_ref

        new_ref2movies = {}
        # ref do not point to itself
        for ref_id, movies in ref2movies.items():
            new_movies = [m_id for m_id in movies if m_id != ref_id]
            if new_movies:
                new_ref2movies[ref_id] = new_movies

        return new_ref2movies

    @staticmethod
    def check_naming(name, other):
        """check_naming
        :param name: 1st name to check
        :param other: 2nd name to check
        :return: True if two names have at least one same word else False
        """
        if name == "\\N" or other == "\\N":
            return True
        names = set(name.split(","))
        names_size = len(names)
        others = set(other.split(","))
        names.update(others)
        # if there are common name in two list (name and other), we say they are same naming
        if len(names) < len(others) + names_size:
            return True
        return False

    @staticmethod
    def save_duplicates(matchings, save_file):
        """save duplicates
        :param matchings: matchings results
        :param save file: output file
        :return: None
        """
        with open(save_file, "a") as output:
            for ref_id, movies in matchings.items():
                line = "\t".join([ref_id] + list(movies)) + "\n"
                output.writelines(line)
        output.close()


def main():
    """ main function """
    parser = argparse.ArgumentParser(description="Find duplication movies.")
    parser.add_argument(
        "--read", type=str, default="movies.tsv", help="tsv file "
    )
    parser.add_argument(
        "--save", type=str, default="duplicates.tsv", help="tsv file "
    )
    args = parser.parse_args()
    finder = DuplicationsFinder()
    df = finder.read_file(args.read)
    finder.process(df=df, output=args.save)


if __name__ == "__main__":
    main()
