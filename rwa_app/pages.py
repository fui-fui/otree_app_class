# rwa_app/pages.py

from otree.api import Page, WaitPage
from .models import Constants, Player  # Cの代わりにConstantsを直接使うように変更

# 質問リスト
QUESTIONS = [
    "伝統的な価値観は現代でも守られるべきだ。",
    "社会の秩序を保つためには、権威に従うべきだ。",
    "子供たちは親や教師の言うことを絶対に守るべきだ。",
    "自由よりも秩序が重要だと感じる。",
    "リーダーには強い姿勢が求められる。",
    "異なる考え方を持つ人は社会の調和を乱すことがある。",
    "政府の命令には従うべきだ。",
    "伝統的な性別役割は大切にすべきだ。",
    "変化よりも安定を求める。",
    "自分と異なる意見はできるだけ避けたいと思う。",
]


class Question(Page):
    form_model = "player"
    form_fields = ["rwa_score"]

    @staticmethod
    def vars_for_template(player: Player):
        # 現在のラウンド番号に合った質問文をテンプレートに渡します
        return dict(
            question_text=QUESTIONS[player.round_number - 1],
            round_number=player.round_number,
            total_rounds=Constants.num_rounds,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 最終ラウンドに到達したときだけ、全ラウンドのスコアを合計します
        if player.round_number == Constants.num_rounds:
            # player.in_all_rounds() で全ラウンドの自分自身の記録を取得できます
            total_score = sum(p.rwa_score for p in player.in_all_rounds())
            # participant.vars は、アプリをまたいで使える一時的な変数入れです
            player.participant.vars["rwa_total"] = total_score


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        score = player.participant.vars["rwa_total"]
        if score <= 19:
            label = "リベラル傾向"
            description = "社会の変化や多様性に寛容な考え方を持っているようです。"
        elif score <= 29:
            label = "ややリベラル"
            description = (
                "一定の秩序を重んじつつも、新しい価値観にもオープンな姿勢が見られます。"
            )
        elif score <= 39:
            label = "やや保守的"
            description = "伝統的な価値観や社会の秩序を重視する傾向がやや見られます。"
        else:
            label = "保守的傾向"
            description = (
                "規範や権威を重視し、社会の安定や秩序を大切にする考え方を持っています。"
            )

        return dict(score=score, label=label, description=description)


class MatchingResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        player_score = player.participant.vars["rwa_total"]

        npc_profiles = [
            {"id": "Aさん", "rwa": 10},
            {"id": "Bさん", "rwa": 20},
            {"id": "Cさん", "rwa": 30},
            {"id": "Dさん", "rwa": 40},
            {"id": "Eさん", "rwa": 50},
        ]

        def calculate_similarity(p_score, n_score):
            diff = abs(p_score - n_score)
            # 分母を 25 にして、差の影響を大きくします。
            similarity_score = (1 - diff / 25) * 100
            # マイナス点にならないように0で下限を設定します
            return round(max(0, similarity_score))

        matches = []
        for npc in npc_profiles:
            similarity = calculate_similarity(player_score, npc["rwa"])
            matches.append(
                dict(id=npc["id"], npc_rwa=npc["rwa"], similarity=similarity)
            )

        player.participant.vars["matches"] = matches
        return dict(matches=matches)


class DictatorGame(Page):
    form_model = "player"
    form_fields = ["allocation"]

    @staticmethod
    def is_displayed(player: Player):
        # dictator_index がマッチング相手の数より少ない間、このページを表示
        # dictator_index は before_next_page で 1 ずつ増える
        if "dictator_index" not in player.participant.vars:
            player.participant.vars["dictator_index"] = 0

        return (
            player.round_number == Constants.num_rounds
            and player.participant.vars["dictator_index"] < Constants.NUM_NPCS
        )

    @staticmethod
    def vars_for_template(player: Player):
        matches = player.participant.vars["matches"]
        current_index = player.participant.vars["dictator_index"]
        npc = matches[current_index]
        return dict(npc=npc)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if "results" not in player.participant.vars:
            player.participant.vars["results"] = []

        matches = player.participant.vars["matches"]
        current_index = player.participant.vars["dictator_index"]
        npc = matches[current_index]

        player.participant.vars["results"].append(
            dict(npc=npc["id"], similarity=npc["similarity"], amount=player.allocation)
        )
        player.participant.vars["dictator_index"] += 1


class Summary(Page):
    @staticmethod
    def is_displayed(player: Player):
        # DictatorGameが全て終わったら表示
        return (
            player.round_number == Constants.num_rounds
            and player.participant.vars.get("dictator_index", 0) >= Constants.NUM_NPCS
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(results=player.participant.vars.get("results"))


# ページ遷移の定義
# DictatorGameを、NPCの数（5回）だけ繰り返すように設定します
page_sequence = (
    [
        Question,
        Results,
        MatchingResults,
    ]
    + [DictatorGame] * Constants.NUM_NPCS
    + [
        Summary,
    ]
)
