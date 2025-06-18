from otree.api import *

# models.py に書いた定数とモデルクラスを読み込む
from .models import C, Subsession, Group, Player

# pages.py に書いた Page クラスと page_sequence を読み込む
from .pages import (
    Question,
    Results,
    MatchingResults,
    DictatorGame,
    Summary,
    page_sequence,
)
