""" this file to find duplication movies """
import argparse

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
def main():
    ...

if __name__ == "__main__":
    main()
