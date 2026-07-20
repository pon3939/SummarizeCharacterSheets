# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

"""
言語
"""


@dataclass
class Language:
    """
    言語
    Attributes:
        Name str: 言語名
        CanTalk bool: 会話
        CanRead bool: 読文
    """

    Name: str
    CanTalk: bool
    CanRead: bool
