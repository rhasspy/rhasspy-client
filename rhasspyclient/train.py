"""
Data structures for training.
"""
from enum import Enum

import attr


class TrainingResult(str, Enum):
    """Result of training a profile."""

    SUCCESS = "success"
    FAILURE = "failure"


@attr.s
class TrainingComplete:
    """Return value from profile training"""

    result: TrainingResult = attr.ib()
    errors: str = attr.ib(default="")
