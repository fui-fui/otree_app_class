# rwa_app/models.py

from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
)


class Constants(BaseConstants):
    name_in_url = "rwa_app"

    # ↓↓↓ グループ分けを不要にするため、Noneに設定します ↓↓↓
    players_per_group = None

    num_rounds = 10

    NUM_NPCS = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    rwa_score = models.IntegerField(
        label="この意見にどのくらい同意しますか？ (1: 全く同意しない〜5: 非常に同意する)",
        choices=[1, 2, 3, 4, 5],
        widget=widgets.RadioSelect,
    )

    allocation = models.CurrencyField(
        label="この相手にいくら配分しますか？ 単位：ポイント", min=0
    )


C = Constants
