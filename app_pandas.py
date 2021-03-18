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

def main():
    ...

if __name__ == "__main__":
    main()
