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
        ...
