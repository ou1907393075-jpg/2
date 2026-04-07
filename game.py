#!/usr/bin/env python3
"""修仙模拟人生文字游戏（命令行版）"""

from __future__ import annotations

import random


STAGES = [
    (0, "凡人"),
    (120, "炼气"),
    (300, "筑基"),
    (600, "金丹"),
    (1000, "元婴"),
    (1600, "化神"),
]

EVENTS = [
    ("山中偶遇灵泉，修为大进。", 30, 0, 0),
    ("闭关时走火入魔，气血受损。", -20, -15, 0),
    ("在坊市淘到低阶丹药。", 10, 0, -8),
    ("斩杀妖兽，获得战利品。", 20, -5, 25),
    ("帮助同门，心境提升。", 15, 5, 0),
]


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.age = 16
        self.hp = 100
        self.cultivation = 0
        self.spirit_stones = 20

    @property
    def stage(self) -> str:
        level = STAGES[0][1]
        for threshold, name in STAGES:
            if self.cultivation >= threshold:
                level = name
        return level

    def info(self) -> str:
        return (
            f"姓名：{self.name}\n"
            f"年龄：{self.age}\n"
            f"境界：{self.stage}\n"
            f"修为：{self.cultivation}\n"
            f"气血：{self.hp}\n"
            f"灵石：{self.spirit_stones}"
        )

    def check_alive(self) -> bool:
        return self.hp > 0


def meditate(player: Player) -> str:
    gain = random.randint(18, 40)
    player.cultivation += gain
    player.hp = max(1, player.hp - random.randint(2, 8))
    return f"你静心吐纳，修为 +{gain}。"


def explore(player: Player) -> str:
    event, cult, hp, stone = random.choice(EVENTS)
    player.cultivation = max(0, player.cultivation + cult)
    player.hp = max(0, min(100, player.hp + hp))
    player.spirit_stones = max(0, player.spirit_stones + stone)
    extra = []
    if cult:
        extra.append(f"修为 {'+' if cult > 0 else ''}{cult}")
    if hp:
        extra.append(f"气血 {'+' if hp > 0 else ''}{hp}")
    if stone:
        extra.append(f"灵石 {'+' if stone > 0 else ''}{stone}")
    return event + ("（" + "，".join(extra) + "）" if extra else "")


def trade(player: Player) -> str:
    if player.spirit_stones < 10:
        return "灵石不足，无法购买丹药。"
    player.spirit_stones -= 10
    recover = random.randint(15, 30)
    player.hp = min(100, player.hp + recover)
    return f"你购买并服下回春丹，气血 +{recover}。"


def age_one_year(player: Player) -> str:
    player.age += 1
    if player.age % 10 == 0:
        player.hp = max(0, player.hp - 10)
        return "岁月流逝，十年关口，气血自然衰减 10。"
    return ""


def run_game() -> None:
    print("=== 修仙模拟人生 ===")
    name = input("请输入道号：").strip() or "无名散修"
    player = Player(name)

    while True:
        if not player.check_alive():
            print("\n你因气血耗尽而陨落，道途止步。")
            break
        if player.cultivation >= 1600:
            print("\n你已踏入化神，名震一方，得道飞升！")
            break

        print("\n" + "-" * 30)
        print(player.info())
        print("\n可选行动：")
        print("1. 打坐修炼")
        print("2. 外出历练")
        print("3. 坊市购丹（10灵石）")
        print("4. 查看状态")
        print("5. 结束游戏")

        choice = input("请选择：").strip()
        if choice == "1":
            print(meditate(player))
        elif choice == "2":
            print(explore(player))
        elif choice == "3":
            print(trade(player))
        elif choice == "4":
            print("\n" + player.info())
            continue
        elif choice == "5":
            print("你收功归山，期待下一世再问长生。")
            break
        else:
            print("无效选择，请输入 1-5。")
            continue

        year_tip = age_one_year(player)
        if year_tip:
            print(year_tip)


if __name__ == "__main__":
    run_game()
