""" this file to find duplication movies """
import argparse
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DuplicationsFinder:
    """Class to find duplication movies"""
