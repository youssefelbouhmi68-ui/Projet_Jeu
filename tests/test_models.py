"""
Tests unitaires (aucune base MongoDB nécessaire).
    python -m unittest discover tests
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Personnage, Monstre, Equipe  # noqa: E402
import game  # noqa: E402
