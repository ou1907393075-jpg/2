#!/usr/bin/env python3
"""高自由度修仙模拟人生（命令行版）- 战斗深化版"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
import json
from pathlib import Path
import random
from typing import Dict, List


LOCATIONS = ["青石镇", "灵溪谷", "白鹿书院", "天火山", "玄霜海", "万剑城"]
FACTIONS = ["散修", "青云宗", "血煞盟", "天机阁", "丹霞谷", "万剑门"]
ROLES = ["商贩", "散修", "炼丹师", "剑修", "医师", "猎妖人", "长老"]
PERSONALITIES = ["豪爽", "谨慎", "孤僻", "热情", "贪财", "正直", "多疑", "仁慈"]
SAVE_PATH = Path("savegame.json")

STAGES = [
    (0, "凡人"),
    (120, "炼气"),
    (320, "筑基"),
    (650, "金丹"),
    (1100, "元婴"),
    (1800, "化神"),
]


@dataclass
class Quest:
    title: str
    giver: str
    location: str
    quest_type: str
    target: int
    progress: int
    reward_stones: int
    reward_rep: int
    done: bool = False

    def detail(self) -> str:
        return (
            f"{self.title}｜发布者:{self.giver}｜地点:{self.location}｜"
            f"进度:{self.progress}/{self.target}｜奖励:灵石{self.reward_stones} 声望{self.reward_rep}"
        )


@dataclass
class NPC:
    name: str
    role: str
    faction: str
    location: str
    personality: str
    age: int = field(default_factory=lambda: random.randint(15, 70))
    hp: int = field(default_factory=lambda: random.randint(50, 100))
    cultivation: int = field(default_factory=lambda: random.randint(0, 900))
    wealth: int = field(default_factory=lambda: random.randint(5, 120))
    relation: int = field(default_factory=lambda: random.randint(-20, 25))
    mood: int = field(default_factory=lambda: random.randint(35, 80))
    beauty: int = field(default_factory=lambda: random.randint(20, 95))
    body_shape: str = field(default_factory=lambda: random.choice(["偏瘦", "匀称", "健壮", "微胖"]))
    talent_grade: str = field(default_factory=lambda: random.choice(["下品", "中品", "上品", "天灵根"]))
    siblings: List[str] = field(default_factory=list)
    temp_status: str = "平稳"
    alive: bool = True

    @property
    def stage(self) -> str:
        current = STAGES[0][1]
        for need, name in STAGES:
            if self.cultivation >= need:
                current = name
        return current


@dataclass
class Enemy:
    name: str
    level: int
    hp: int
    qi: int
    attack: int
    defense: int
    agility: int
    reward_stones: int
    reward_cultivation: int
    biography: str
    temperament: str


@dataclass
class Child:
    name: str
    age: int
    talent: int
    destiny: str = "平凡"


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.age = 16
        self.max_hp = 120
        self.hp = 120
        self.max_qi = 80
        self.qi = 80
        self.cultivation = 0
        self.stones = 30
        self.reputation = 0
        self.karma = 0
        self.location = random.choice(LOCATIONS)
        self.faction = "散修"
        self.inventory: Dict[str, int] = {"回春丹": 1, "灵米": 2}
        self.social: Dict[str, int] = {}
        self.active_quests: List[Quest] = []
        self.party: List[str] = []
        self.weapon_bonus = 0
        self.armor_bonus = 0
        self.weapon_name = "凡铁剑"
        self.armor_name = "布衣"
        self.artifact: str | None = None
        self.artifact_charge = 0
        self.title = "无名散修"
        self.spouse: str | None = None
        self.children: List[Child] = []
        self.clan_name = f"{name}家"
        self.clan_prestige = 0

    @property
    def stage(self) -> str:
        current = STAGES[0][1]
        for need, name in STAGES:
            if self.cultivation >= need:
                current = name
        return current

    @property
    def attack(self) -> int:
        return 12 + self.cultivation // 40 + self.weapon_bonus

    @property
    def defense(self) -> int:
        return 6 + self.cultivation // 65 + self.armor_bonus

    @property
    def agility(self) -> int:
        return 10 + self.cultivation // 70

    @property
    def crit_rate(self) -> float:
        return min(0.4, 0.08 + self.cultivation / 4500)

    def recover_small(self) -> None:
        self.hp = min(self.max_hp, self.hp + 6)
        self.qi = min(self.max_qi, self.qi + 10)

    def is_alive(self) -> bool:
        return self.hp > 0

    def summary(self) -> str:
        items = "、".join(f"{k}x{v}" for k, v in self.inventory.items() if v > 0) or "无"
        return (
            f"道号：{self.name}\n"
            f"年龄：{self.age}\n"
            f"地点：{self.location}\n"
            f"称号：{self.title}\n"
            f"家族：{self.clan_name}（家族声望 {self.clan_prestige}）\n"
            f"阵营：{self.faction}\n"
            f"境界：{self.stage}（修为 {self.cultivation}）\n"
            f"气血：{self.hp}/{self.max_hp}\n"
            f"真气：{self.qi}/{self.max_qi}\n"
            f"攻击/防御/身法：{self.attack}/{self.defense}/{self.agility}\n"
            f"灵石：{self.stones}\n"
            f"声望：{self.reputation}\n"
            f"因果值：{self.karma}\n"
            f"装备加成：攻击+{self.weapon_bonus} 防御+{self.armor_bonus}\n"
            f"装备：{self.weapon_name}/{self.armor_name}｜法宝：{self.artifact or '无'}（充能 {self.artifact_charge}/3）\n"
            f"道侣：{self.spouse or '暂无'}｜子嗣：{len(self.children)}\n"
            f"队伍：{'、'.join(self.party) if self.party else '无'}\n"
            f"背包：{items}"
        )


class World:
    def __init__(self, player_name: str) -> None:
        self.turn = 1
        self.player = Player(player_name)
        self.npcs = self._generate_npcs(22)
        self._assign_sibling_links()
        self.log: List[str] = []

    def _generate_npcs(self, count: int) -> List[NPC]:
        surname = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨")
        given = ["青", "月", "霜", "烈", "云", "川", "宁", "竹", "澜", "墨", "玄", "雪", "风", "瑶"]
        npcs = []
        for _ in range(count):
            name = random.choice(surname) + random.choice(given) + random.choice(given)
            npcs.append(
                NPC(
                    name=name,
                    role=random.choice(ROLES),
                    faction=random.choice(FACTIONS),
                    location=random.choice(LOCATIONS),
                    personality=random.choice(PERSONALITIES),
                )
            )
        return npcs

    def _assign_sibling_links(self) -> None:
        if len(self.npcs) < 4:
            return
        pool = self.npcs[:]
        random.shuffle(pool)
        for i in range(0, len(pool) - 1, 6):
            a = pool[i]
            b = pool[i + 1]
            if b.name not in a.siblings:
                a.siblings.append(b.name)
            if a.name not in b.siblings:
                b.siblings.append(a.name)

    def npcs_here(self) -> List[NPC]:
        return [n for n in self.npcs if n.alive and n.location == self.player.location]

    def random_alive_npc(self) -> NPC | None:
        alive = [n for n in self.npcs if n.alive]
        return random.choice(alive) if alive else None

    def tick_world(self) -> None:
        self.turn += 1
        self.player.age += 1
        self.player.recover_small()
        self.player.artifact_charge = min(3, self.player.artifact_charge + 1)
        self._family_tick()
        self._age_penalty()

        for npc in self.npcs:
            if not npc.alive:
                continue
            npc.age += 1
            npc.mood = max(0, min(100, npc.mood + random.randint(-8, 8)))
            npc.cultivation = max(0, npc.cultivation + random.randint(-12, 25))
            if random.random() < 0.18:
                npc.body_shape = random.choice(["偏瘦", "匀称", "健壮", "微胖"])
            if random.random() < 0.2:
                npc.temp_status = random.choice(["闭关中", "负伤", "历练中", "平稳", "心境不宁"])
            if random.random() < 0.45:
                npc.location = random.choice(LOCATIONS)
            if npc.age > 95 and random.random() < 0.18:
                npc.alive = False
                self.log.append(f"{npc.name} 寿元将尽，坐化于 {npc.location}。")

        self._update_quest_progress()
        self._spawn_npc_if_needed()
        self._npc_world_event()
        self._karma_event()
        self._major_world_event()

    def _family_tick(self) -> None:
        for child in self.player.children:
            child.age += 1
            if child.age in (12, 16):
                gain = random.randint(2, 6)
                self.player.clan_prestige += gain
                self.log.append(f"家族子嗣 {child.name} 在修行上展露锋芒，家族声望 +{gain}。")

    def _age_penalty(self) -> None:
        if self.player.age % 12 == 0:
            self.player.hp = max(0, self.player.hp - 8)
            self.log.append("岁月侵蚀肉身，你在一个甲子前的旧伤隐隐作痛（气血 -8）。")

    def _update_quest_progress(self) -> None:
        for q in self.player.active_quests:
            if q.done:
                continue
            if q.quest_type == "历练":
                q.progress = min(q.target, q.progress + random.randint(0, 2))
            elif q.quest_type == "社交":
                q.progress = min(q.target, q.progress + random.randint(0, 1))
            elif q.quest_type == "修炼":
                q.progress = min(q.target, q.progress + random.randint(0, 3))

    def _spawn_npc_if_needed(self) -> None:
        alive_count = sum(1 for n in self.npcs if n.alive)
        if alive_count >= 18:
            return
        recruit = self._generate_npcs(1)[0]
        self.npcs.append(recruit)
        self.log.append(f"江湖新秀 {recruit.name}（{recruit.role}）初入修真界，出现在 {recruit.location}。")

    def _npc_world_event(self) -> None:
        a = self.random_alive_npc()
        b = self.random_alive_npc()
        if not a or not b or a.name == b.name:
            return
        event_roll = random.random()
        if event_roll < 0.22:
            a.relation = min(100, a.relation + 6)
            b.relation = min(100, b.relation + 6)
            self.log.append(f"{a.name} 与 {b.name} 结伴历练，交情渐深。")
        elif event_roll < 0.36:
            a.relation = max(-100, a.relation - 8)
            b.relation = max(-100, b.relation - 8)
            self.log.append(f"{a.name} 与 {b.name} 因秘境机缘起争执，关系恶化。")
        elif event_roll < 0.43:
            self.log.append(f"{a.name} 在 {a.location} 开设小铺，广收灵材。")

    def _karma_event(self) -> None:
        p = self.player
        if p.karma >= 15 and random.random() < 0.22:
            p.hp = max(0, p.hp - 10)
            self.log.append("你因果缠身，遭遇心魔反噬（气血 -10）。")
        elif p.karma <= -15 and random.random() < 0.22:
            p.cultivation += 20
            self.log.append("你善缘汇聚，顿悟一丝天机（修为 +20）。")

    def _major_world_event(self) -> None:
        if self.turn % 5 != 0:
            return
        p = self.player
        event = random.choice(["秘境喷发", "宗门大比", "商路复苏", "妖潮来袭"])
        if event == "秘境喷发":
            gain = random.randint(20, 45)
            p.cultivation += gain
            self.log.append(f"天地异动，秘境喷发，你趁机悟道（修为 +{gain}）。")
        elif event == "宗门大比":
            rep = random.randint(2, 6)
            p.reputation += rep
            self.log.append(f"你在宗门大比中崭露头角（声望 +{rep}）。")
        elif event == "商路复苏":
            stones = random.randint(15, 35)
            p.stones += stones
            self.log.append(f"商路复苏，家族生意兴盛（灵石 +{stones}）。")
        else:
            p.hp = max(1, p.hp - random.randint(6, 14))
            p.clan_prestige += random.randint(1, 4)
            self.log.append("妖潮扰境，你护住族人，家族声望提升但自身受伤。")

    def show_world_news(self) -> str:
        if not self.log:
            return "近况平静，没有大事发生。"
        return "\n".join(f"- {line}" for line in self.log[-6:])


def generate_enemy(player: Player, location: str) -> Enemy:
    base = max(1, player.cultivation // 120 + 1)
    factor = {
        "青石镇": 0.8,
        "白鹿书院": 0.9,
        "灵溪谷": 1.0,
        "万剑城": 1.1,
        "玄霜海": 1.2,
        "天火山": 1.35,
    }.get(location, 1.0)
    level = max(1, int(base * factor))
    templates = [
        ("噬骨狼", "曾是山林狼王，被邪气侵蚀后失去族群", "凶暴"),
        ("赤眼妖狐", "年幼时巢穴被毁，长期流窜于边境", "狡诈"),
        ("黑鳞蝠王", "在古矿洞中吞食灵石成长，守着旧巢", "贪婪"),
        ("邪修傀儡", "前朝修士遗留的禁术造物，只执行残命", "冷漠"),
        ("岩甲蜥", "常年潜伏熔岩裂隙，为护幼崽而极度好斗", "固执"),
        ("幽魂剑侍", "生前是剑客，执念未消，徘徊古战场", "偏执"),
    ]
    name, bio, temper = random.choice(templates)
    if random.random() < 0.45:
        bio += " 传闻其仍在寻找失散的同族兄弟。"
    hp = 70 + level * random.randint(14, 22)
    qi = 40 + level * random.randint(8, 14)
    attack = 9 + level * random.randint(3, 5)
    defense = 4 + level * random.randint(2, 4)
    agility = 8 + level * random.randint(1, 3)
    return Enemy(
        name=name,
        level=level,
        hp=hp,
        qi=qi,
        attack=attack,
        defense=defense,
        agility=agility,
        reward_stones=12 + level * random.randint(6, 11),
        reward_cultivation=10 + level * random.randint(10, 18),
        biography=bio,
        temperament=temper,
    )


def damage_calc(attack: int, defense: int, crit: bool = False, guard: bool = False) -> int:
    base = max(1, attack - defense // 2 + random.randint(-3, 5))
    if crit:
        base = int(base * 1.6)
    if guard:
        base = int(base * 0.55)
    return max(1, base)


def player_skill_attack(player: Player, enemy: Enemy, skill: str) -> tuple[int, int, str]:
    if skill == "裂风斩":
        cost = 18
        if player.qi < cost:
            return 0, 0, "真气不足，施法失败。"
        player.qi -= cost
        crit = random.random() < player.crit_rate + 0.08
        dmg = damage_calc(player.attack + 10, enemy.defense, crit=crit)
        return dmg, 0, f"你施展裂风斩，造成 {dmg} 点伤害{'（暴击）' if crit else ''}。"

    if skill == "玄冰护体":
        cost = 12
        if player.qi < cost:
            return 0, 0, "真气不足，护体失败。"
        player.qi -= cost
        heal = random.randint(8, 18)
        player.hp = min(player.max_hp, player.hp + heal)
        return 0, 1, f"你运转玄冰护体，气血 +{heal}，并获得一回合减伤。"

    if skill == "焚心诀":
        cost = 22
        if player.qi < cost:
            return 0, 0, "真气不足，无法引动焚心诀。"
        player.qi -= cost
        dmg = damage_calc(player.attack + 16, enemy.defense)
        recoil = random.randint(4, 10)
        player.hp = max(1, player.hp - recoil)
        return dmg, 0, f"你燃烧精血催动焚心诀，造成 {dmg} 点伤害，自损 {recoil} 点气血。"

    return 0, 0, "未知技能。"


def unlocked_skills(player: Player) -> List[str]:
    skills = ["裂风斩", "玄冰护体"]
    if player.cultivation >= 600:
        skills.append("焚心诀")
    return skills


def use_item_in_battle(player: Player) -> str:
    if player.inventory.get("回春丹", 0) > 0:
        player.inventory["回春丹"] -= 1
        if player.inventory["回春丹"] <= 0:
            del player.inventory["回春丹"]
        heal = random.randint(20, 35)
        player.hp = min(player.max_hp, player.hp + heal)
        return f"你服下回春丹，气血 +{heal}。"
    return "你没有可用的回春丹。"


def use_artifact_in_battle(player: Player, enemy: Enemy) -> tuple[int, int, str]:
    if not player.artifact:
        return 0, 0, "你尚未持有法宝。"
    if player.artifact_charge <= 0:
        return 0, 0, "法宝尚未充能完成。"

    player.artifact_charge -= 1
    if player.artifact == "玄雷印":
        dmg = damage_calc(player.attack + 20, enemy.defense, crit=True)
        return dmg, 0, f"玄雷印引动雷霆，轰击造成 {dmg} 点伤害。"
    if player.artifact == "青莲灯":
        heal = random.randint(18, 30)
        player.hp = min(player.max_hp, player.hp + heal)
        return 0, 1, f"青莲灯绽放灵光，你恢复 {heal} 点气血并获得减伤。"
    if player.artifact == "时砂镜":
        player.qi = min(player.max_qi, player.qi + 12)
        return 0, 2, "时砂镜扭转瞬息，你回气并获得两回合减伤。"
    return 0, 0, "法宝回应微弱，未触发效果。"


def get_auto_companions(world: World) -> List[NPC]:
    p = world.player
    if p.party:
        party_members = [n for n in world.npcs if n.name in p.party and n.alive and n.location == p.location]
        if party_members:
            return party_members[:2]
    candidates = [n for n in world.npcs_here() if p.social.get(n.name, 0) >= 25 and n.alive]
    candidates.sort(key=lambda n: p.social.get(n.name, 0), reverse=True)
    return candidates[:2]


def companion_act(companion: NPC, enemy: Enemy) -> tuple[int, int, str]:
    mood_shift = random.randint(-5, 5)
    companion.mood = max(0, min(100, companion.mood + mood_shift))
    temper = companion.personality
    roll = random.random()
    if temper in ("谨慎", "多疑") and roll < 0.25:
        return 0, 1, f"{companion.name} 观察战局，选择护法牵制敌人。"
    if temper in ("孤僻", "贪财") and roll < 0.20:
        return 0, 0, f"{companion.name} 犹豫片刻，没有贸然出手。"
    if temper in ("热情", "豪爽") and roll < 0.30:
        dmg = damage_calc(12 + companion.cultivation // 55, enemy.defense, crit=True)
        return dmg, 0, f"{companion.name} 豪气冲阵，重击造成 {dmg} 伤害。"
    dmg = damage_calc(10 + companion.cultivation // 65, enemy.defense)
    return dmg, 0, f"{companion.name} 协同出手，造成 {dmg} 伤害。"


def battle_enemy(world: World, enemy: Enemy) -> tuple[bool, str]:
    p = world.player
    guard = 0
    companions = get_auto_companions(world)
    team_intro = (
        "你并肩作战的同伴：" + "、".join(c.name for c in companions)
        if companions
        else "这一战你只能独自应对。"
    )
    log: List[str] = [f"遭遇 {enemy.name}（Lv.{enemy.level}）！", f"敌方经历：{enemy.biography}", f"敌方性情：{enemy.temperament}", team_intro]

    while enemy.hp > 0 and p.hp > 0:
        print("\n--- 战斗回合 ---")
        print(f"你：HP {p.hp}/{p.max_hp} | QI {p.qi}/{p.max_qi}")
        print(f"敌：HP {enemy.hp} | QI {enemy.qi}")
        print("1. 普攻  2. 技能  3. 防御  4. 使用丹药  5. 尝试逃跑  6. 法宝")
        choice = input("选择战斗操作：").strip() or "1"

        if choice == "1":
            crit = random.random() < p.crit_rate
            dmg = damage_calc(p.attack, enemy.defense, crit=crit)
            enemy.hp = max(0, enemy.hp - dmg)
            log.append(f"你挥剑斩击，造成 {dmg} 伤害{'（暴击）' if crit else ''}。")
        elif choice == "2":
            skills = unlocked_skills(p)
            print("可用技能：")
            for i, s in enumerate(skills, 1):
                print(f"{i}. {s}")
            pick = input("技能编号：").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(skills):
                dmg, g, msg = player_skill_attack(p, enemy, skills[int(pick) - 1])
                enemy.hp = max(0, enemy.hp - dmg)
                guard = max(guard, g)
                log.append(msg)
            else:
                log.append("你分神了，错失出手机会。")
        elif choice == "3":
            guard = max(guard, 1)
            p.qi = min(p.max_qi, p.qi + 6)
            log.append("你稳住身形，摆出防御架势（本回合减伤）。")
        elif choice == "4":
            log.append(use_item_in_battle(p))
        elif choice == "5":
            chance = 0.3 + (p.agility - enemy.agility) * 0.02
            if random.random() < max(0.1, min(0.75, chance)):
                log.append("你抓住破绽成功脱离战斗。")
                return False, "\n".join(log)
            log.append("逃跑失败，被敌人缠住！")
        elif choice == "6":
            dmg, g, msg = use_artifact_in_battle(p, enemy)
            enemy.hp = max(0, enemy.hp - dmg)
            guard = max(guard, g)
            log.append(msg)
        else:
            log.append("你动作迟疑，露出破绽。")

        if enemy.hp <= 0:
            break

        for companion in companions:
            if enemy.hp <= 0:
                break
            dmg, ally_guard, msg = companion_act(companion, enemy)
            enemy.hp = max(0, enemy.hp - dmg)
            guard = max(guard, ally_guard)
            log.append(msg)

        enemy_skill_roll = random.random()
        skill_bias = 0.25
        if enemy.temperament in ("狡诈", "偏执"):
            skill_bias = 0.4
        elif enemy.temperament in ("冷漠", "固执"):
            skill_bias = 0.2
        if enemy_skill_roll < skill_bias and enemy.qi >= 12:
            enemy.qi -= 12
            dmg = damage_calc(enemy.attack + 7, p.defense, guard=guard > 0)
            p.hp = max(0, p.hp - dmg)
            log.append(f"{enemy.name} 释放妖力冲击，你受到 {dmg} 点伤害。")
        else:
            crit = random.random() < 0.08 + enemy.level * 0.01
            dmg = damage_calc(enemy.attack, p.defense, crit=crit, guard=guard > 0)
            p.hp = max(0, p.hp - dmg)
            log.append(f"{enemy.name} 发动扑杀，你受到 {dmg} 点伤害{'（暴击）' if crit else ''}。")

        guard = max(0, guard - 1)

    if p.hp > 0:
        p.cultivation += enemy.reward_cultivation
        p.stones += enemy.reward_stones
        p.reputation += 2
        p.karma -= 1
        _advance_quest_by_type(p, "历练", 2)
        log.append(
            f"你击败 {enemy.name}！获得灵石 +{enemy.reward_stones}，修为 +{enemy.reward_cultivation}，声望 +2，因果 -1。"
        )
        return True, "\n".join(log)

    log.append("你战败倒地，命悬一线。")
    return False, "\n".join(log)


def meditate(world: World) -> str:
    p = world.player
    gain = random.randint(18, 42)
    p.cultivation += gain
    p.qi = min(p.max_qi, p.qi + random.randint(10, 20))
    p.hp = max(1, p.hp - random.randint(2, 8))
    if random.random() < 0.2:
        p.reputation += 1
    _advance_quest_by_type(p, "修炼", random.randint(1, 2))
    return f"你在 {p.location} 吐纳周天，修为 +{gain}，真气有所恢复。"


def roam(world: World) -> str:
    p = world.player
    dest = random.choice([loc for loc in LOCATIONS if loc != p.location])
    p.location = dest
    p.hp = max(1, p.hp - 2)
    p.qi = min(p.max_qi, p.qi + 4)
    _advance_quest_by_type(p, "历练", 1)
    return f"你御风远行，抵达 {dest}。长途奔波，气血 -2。"


def work_or_hunt(world: World) -> str:
    p = world.player
    enemy = generate_enemy(p, p.location)
    win, battle_log = battle_enemy(world, enemy)
    if win:
        return battle_log

    if p.hp <= 0:
        return battle_log

    # 逃跑/中断时的保底收益或惩罚
    p.stones += random.randint(2, 8)
    p.karma += 1
    return battle_log + "\n你仓促撤离，捡回些许战利（灵石少量），因果 +1。"


def consume_item(world: World) -> str:
    p = world.player
    if not p.inventory:
        return "背包空空如也。"

    print("可用物品：")
    items = [(k, v) for k, v in p.inventory.items() if v > 0]
    for i, (name, cnt) in enumerate(items, 1):
        print(f"{i}. {name} x{cnt}")
    choice = input("选择物品编号（回车取消）：").strip()
    if not choice:
        return "你暂时没有使用任何物品。"
    if not choice.isdigit() or not (1 <= int(choice) <= len(items)):
        return "选择无效。"

    name, _ = items[int(choice) - 1]
    p.inventory[name] -= 1
    if p.inventory[name] <= 0:
        del p.inventory[name]

    if name == "回春丹":
        heal = random.randint(22, 36)
        p.hp = min(p.max_hp, p.hp + heal)
        return f"丹药入腹，气血 +{heal}。"
    if name == "灵米":
        p.hp = min(p.max_hp, p.hp + 8)
        p.qi = min(p.max_qi, p.qi + 8)
        return "你吃下灵米，恢复气血与真气。"
    return f"你使用了 {name}，感觉状态略有变化。"


def npc_duel(world: World, npc: NPC) -> str:
    enemy = Enemy(
        name=f"{npc.name}（切磋）",
        level=max(1, npc.cultivation // 130 + 1),
        hp=80 + npc.cultivation // 12,
        qi=50,
        attack=10 + npc.cultivation // 50,
        defense=6 + npc.cultivation // 70,
        agility=10 + npc.cultivation // 80,
        reward_stones=0,
        reward_cultivation=18,
        biography=f"{npc.name} 出身 {npc.faction}，性格 {npc.personality}。",
        temperament="谨慎" if npc.personality in ("谨慎", "多疑") else "好战",
    )
    win, log = battle_enemy(world, enemy)
    p = world.player
    if win:
        p.reputation += 2
        p.social[npc.name] = p.social.get(npc.name, 0) + 3
        return log + "\n这场切磋让你名声渐起。"

    if p.hp > 0:  # 逃跑算输
        p.social[npc.name] = p.social.get(npc.name, 0) - 2
        return log + "\n你未能完成切磋，对方略感失望。"

    p.social[npc.name] = p.social.get(npc.name, 0) - 5
    return log


def meet_npc(world: World) -> str:
    p = world.player
    local = world.npcs_here()
    if not local:
        return "此地今日无人来往，你独自对月而坐。"

    print("你遇到以下人物：")
    for i, npc in enumerate(local[:8], 1):
        rel = p.social.get(npc.name, 0)
        sib = f"，亲属:{'、'.join(npc.siblings)}" if npc.siblings else ""
        print(
            f"{i}. {npc.name}（{npc.role}，{npc.faction}，{npc.stage}，好感 {rel}，{npc.body_shape}，颜值{npc.beauty}，资质{npc.talent_grade}，状态{npc.temp_status}{sib}）"
        )

    choice = input("选择互动对象（回车随机）：").strip()
    target = random.choice(local)
    if choice.isdigit() and 1 <= int(choice) <= min(8, len(local)):
        target = local[int(choice) - 1]

    mode = input("互动：1结交 2切磋战斗 3交易 4打探 5接任务：").strip() or "1"
    rel = p.social.get(target.name, 0)

    if mode == "1":
        delta = random.randint(4, 14)
        p.social[target.name] = rel + delta
        target.relation += delta // 2
        _advance_quest_by_type(p, "社交", 1)
        if random.random() < 0.25:
            p.inventory["回春丹"] = p.inventory.get("回春丹", 0) + 1
            gift = " 对方赠你一枚回春丹。"
        else:
            gift = ""
        return f"你与 {target.name} 畅谈修行心得，好感 +{delta}。{gift}"

    if mode == "2":
        return npc_duel(world, target)

    if mode == "3":
        if p.stones < 15:
            return "你灵石不足，交易未成。"
        p.stones -= 15
        p.inventory["回春丹"] = p.inventory.get("回春丹", 0) + 1
        p.social[target.name] = rel + 1
        return f"你向 {target.name} 购得回春丹一枚（灵石 -15）。"

    if mode == "4":
        tip = random.choice([
            "天火山将有秘境松动。",
            "青云宗最近在招收外门弟子。",
            "万剑城黑市有人高价收妖丹。",
            "玄霜海近来妖潮频发，谨慎前往。",
        ])
        p.social[target.name] = rel + 2
        return f"{target.name} 低声告诉你：{tip}"

    quest = create_quest(target.name, p.location)
    p.active_quests.append(quest)
    p.social[target.name] = rel + 2
    return f"{target.name} 委托你：{quest.detail()}"


def create_quest(giver: str, location: str) -> Quest:
    qtype = random.choice(["历练", "社交", "修炼"])
    if qtype == "历练":
        return Quest("清剿附近妖患", giver, location, qtype, target=6, progress=0, reward_stones=42, reward_rep=4)
    if qtype == "社交":
        return Quest("联络散修盟友", giver, location, qtype, target=4, progress=0, reward_stones=30, reward_rep=5)
    return Quest("闭关小成", giver, location, qtype, target=8, progress=0, reward_stones=34, reward_rep=3)


def quest_center(world: World) -> str:
    p = world.player
    if not p.active_quests:
        return "你当前没有任务。可以在 NPC 互动中接取。"

    print("当前任务：")
    for i, q in enumerate(p.active_quests, 1):
        status = "已完成" if q.done or q.progress >= q.target else "进行中"
        print(f"{i}. [{status}] {q.detail()}")

    choice = input("输入任务编号尝试提交（回车返回）：").strip()
    if not choice:
        return "你查看了任务进度。"
    if not choice.isdigit() or not (1 <= int(choice) <= len(p.active_quests)):
        return "输入无效。"

    q = p.active_quests[int(choice) - 1]
    if q.progress < q.target and not q.done:
        return "任务尚未达成。"

    q.done = True
    p.stones += q.reward_stones
    p.reputation += q.reward_rep
    p.karma -= 1
    p.active_quests.pop(int(choice) - 1)
    return f"你交付任务【{q.title}】，获得灵石 +{q.reward_stones}、声望 +{q.reward_rep}、因果 -1。"


def _advance_quest_by_type(player: Player, quest_type: str, delta: int) -> None:
    for q in player.active_quests:
        if q.quest_type == quest_type and not q.done:
            q.progress = min(q.target, q.progress + delta)


def update_player_title(player: Player) -> None:
    if player.cultivation >= 1800:
        player.title = "化神真君"
    elif player.clan_prestige >= 80:
        player.title = "一族之主"
    elif player.reputation >= 60:
        player.title = "名动一方"
    elif player.cultivation >= 650:
        player.title = "金丹上人"
    elif player.cultivation >= 320:
        player.title = "筑基修士"
    elif player.reputation >= 20:
        player.title = "小有名气"
    else:
        player.title = "无名散修"


def market(world: World) -> str:
    p = world.player
    print("坊市摊位：")
    print("1. 回春丹（15灵石）")
    print("2. 灵米（5灵石）")
    print("3. 玄铁剑（60灵石，攻击+4，唯一）")
    print("4. 玄龟甲（60灵石，防御+3，唯一）")
    print("5. 聚气符（80灵石，真气上限+10，最多两次）")
    print("6. 法宝匣（120灵石，随机获得法宝）")
    print("7. 炼器强化（50灵石，随机强化武器或护甲）")
    choice = input("选择购买编号（回车取消）：").strip()
    if not choice:
        return "你逛了一圈坊市，暂时没有出手。"

    if choice == "1":
        if p.stones < 15:
            return "灵石不足。"
        p.stones -= 15
        p.inventory["回春丹"] = p.inventory.get("回春丹", 0) + 1
        return "你购买了回春丹。"
    if choice == "2":
        if p.stones < 5:
            return "灵石不足。"
        p.stones -= 5
        p.inventory["灵米"] = p.inventory.get("灵米", 0) + 1
        return "你购买了一份灵米。"
    if choice == "3":
        if p.weapon_bonus >= 4:
            return "你已经有更好的武器了。"
        if p.stones < 60:
            return "灵石不足。"
        p.stones -= 60
        p.weapon_bonus = 4
        p.weapon_name = "玄铁剑"
        return "你换上玄铁剑，攻击提升。"
    if choice == "4":
        if p.armor_bonus >= 3:
            return "你已经有更好的护甲了。"
        if p.stones < 60:
            return "灵石不足。"
        p.stones -= 60
        p.armor_bonus = 3
        p.armor_name = "玄龟甲"
        return "你披上玄龟甲，防御提升。"
    if choice == "5":
        if p.max_qi >= 100:
            return "你的经脉暂时无法再承受聚气符。"
        if p.stones < 80:
            return "灵石不足。"
        p.stones -= 80
        p.max_qi += 10
        p.qi = min(p.max_qi, p.qi + 10)
        return "你炼化聚气符，真气上限提升 +10。"
    if choice == "6":
        if p.stones < 120:
            return "灵石不足。"
        p.stones -= 120
        p.artifact = random.choice(["玄雷印", "青莲灯", "时砂镜"])
        p.artifact_charge = 3
        return f"你开启法宝匣，获得法宝【{p.artifact}】（充能已满）。"
    if choice == "7":
        if p.stones < 50:
            return "灵石不足。"
        p.stones -= 50
        if random.random() < 0.5:
            up = random.randint(1, 2)
            p.weapon_bonus += up
            return f"炼器师淬炼了你的武器，攻击加成 +{up}。"
        up = random.randint(1, 2)
        p.armor_bonus += up
        return f"炼器师加固了你的护甲，防御加成 +{up}。"
    return "摊主没听懂你的需求。"


def family_hall(world: World) -> str:
    p = world.player
    print("家族事务：")
    print("1. 设定/更改家族名")
    print("2. 寻觅道侣")
    print("3. 生儿育女")
    print("4. 查看家族成员")
    print("5. 培养子嗣（消耗灵石）")
    choice = input("选择编号（回车返回）：").strip()
    if not choice:
        return "你在家族祠堂中静坐片刻。"

    if choice == "1":
        name = input("输入新的家族名（如“苏家”）：").strip()
        if not name:
            return "家族名未变更。"
        p.clan_name = name
        return f"家族更名完成：{name}。"

    if choice == "2":
        if p.spouse:
            return f"你已与 {p.spouse} 结为道侣。"
        candidates = [n for n in world.npcs_here() if p.social.get(n.name, 0) >= 20]
        if not candidates:
            return "当前没有足够亲近的对象（需同地点且好感≥20）。"
        print("可结缘对象：")
        for i, npc in enumerate(candidates[:6], 1):
            print(f"{i}. {npc.name}（{npc.faction}，好感 {p.social.get(npc.name, 0)}）")
        pick = input("选择编号：").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= min(6, len(candidates))):
            return "你最终没有做出决定。"
        target = candidates[int(pick) - 1]
        p.spouse = target.name
        p.clan_prestige += 5
        return f"你与 {target.name} 缔结道侣，家族声望 +5。"

    if choice == "3":
        if not p.spouse:
            return "你尚无道侣，难谈传承。"
        if len(p.children) >= 6:
            return "你已有不少子嗣，决定先专注培养。"
        success = random.random() < 0.7
        if not success:
            return "这几年机缘未至，暂未添丁。"
        names = ["清禾", "凌川", "若雪", "子衿", "玄烨", "听雨", "少宁", "知寒"]
        destiny = random.choice(["平凡", "灵根上品", "剑心通明", "丹道天赋", "福缘深厚"])
        child = Child(name=random.choice(names), age=0, talent=random.randint(55, 95), destiny=destiny)
        p.children.append(child)
        p.clan_prestige += 8
        return f"家中迎来新生命：{child.name}（{child.destiny}），家族声望 +8。"

    if choice == "4":
        if not p.children:
            return f"道侣：{p.spouse or '暂无'}。目前尚无子嗣。"
        lines = [f"道侣：{p.spouse or '暂无'}", "子嗣列表："]
        for child in p.children:
            lines.append(f"- {child.name}｜年龄:{child.age}｜资质:{child.talent}｜命格:{child.destiny}")
        return "\n".join(lines)

    if choice == "5":
        if not p.children:
            return "你尚无子嗣可培养。"
        if p.stones < 30:
            return "灵石不足，无法组织家族培养。"
        p.stones -= 30
        child = random.choice(p.children)
        boost = random.randint(2, 6)
        child.talent = min(100, child.talent + boost)
        p.clan_prestige += random.randint(2, 5)
        return f"你重点培养了 {child.name}，资质 +{boost}，家族声望小幅提升。"

    return "家族事务暂且搁置。"


def pass_to_heir(world: World) -> str:
    p = world.player
    if not p.children:
        return "你尚无可继承衣钵的子嗣。"
    print("可传位子嗣：")
    for i, child in enumerate(p.children, 1):
        print(f"{i}. {child.name}（年龄{child.age}，资质{child.talent}，命格{child.destiny}）")
    pick = input("选择继承人编号：").strip()
    if not pick.isdigit() or not (1 <= int(pick) <= len(p.children)):
        return "你最终没有完成传位。"

    heir = p.children.pop(int(pick) - 1)
    p.name = heir.name
    p.age = max(16, heir.age)
    p.cultivation = max(60, heir.talent * 3)
    p.max_hp = 100 + heir.talent // 2
    p.hp = p.max_hp
    p.max_qi = 70 + heir.talent // 3
    p.qi = p.max_qi
    p.reputation = max(0, p.reputation // 2 + p.clan_prestige // 10)
    p.title = "少主继位"
    p.karma = max(-10, min(10, p.karma // 2))
    p.stones += random.randint(20, 60)
    p.social = {}
    return f"你将家业传给 {heir.name}，新一代家主正式踏上修行路。"


def manage_party(world: World) -> str:
    p = world.player
    here = [n for n in world.npcs_here() if n.alive]
    print("队伍管理：")
    print("1. 邀请同伴入队（需同地点且好感≥35）")
    print("2. 让队友离队")
    print("3. 查看当前队友详情")
    choice = input("选择编号（回车返回）：").strip()
    if not choice:
        return "你重新整理了行囊与队形。"

    if choice == "1":
        candidates = [n for n in here if p.social.get(n.name, 0) >= 35 and n.name not in p.party]
        if not candidates:
            return "没有愿意入队的高好感 NPC。"
        for i, npc in enumerate(candidates[:5], 1):
            print(f"{i}. {npc.name}｜好感{p.social.get(npc.name, 0)}｜{npc.body_shape}｜颜值{npc.beauty}｜资质{npc.talent_grade}")
        pick = input("选择入队编号：").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= min(5, len(candidates))):
            return "你暂时没有邀请成功。"
        target = candidates[int(pick) - 1]
        p.party.append(target.name)
        return f"{target.name} 加入了你的队伍。"

    if choice == "2":
        if not p.party:
            return "当前没有队友。"
        for i, name in enumerate(p.party, 1):
            print(f"{i}. {name}")
        pick = input("选择离队编号：").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= len(p.party)):
            return "离队操作取消。"
        name = p.party.pop(int(pick) - 1)
        return f"{name} 已离队。"

    if choice == "3":
        if not p.party:
            return "当前队伍为空。"
        lines = ["当前队友："]
        for name in p.party:
            npc = next((n for n in world.npcs if n.name == name and n.alive), None)
            if not npc:
                lines.append(f"- {name}（暂时失联）")
                continue
            sib = f"，兄弟姐妹：{'、'.join(npc.siblings)}" if npc.siblings else ""
            lines.append(
                f"- {npc.name}｜{npc.role}/{npc.faction}｜{npc.body_shape}｜颜值{npc.beauty}｜资质{npc.talent_grade}｜状态{npc.temp_status}{sib}"
            )
        return "\n".join(lines)
    return "你保持当前队伍配置。"


def join_faction(world: World) -> str:
    p = world.player
    if p.faction != "散修":
        return f"你已在 {p.faction} 门下修行。"
    print("可加入阵营：")
    choices = [f for f in FACTIONS if f != "散修"]
    for i, f in enumerate(choices, 1):
        print(f"{i}. {f}")
    pick = input("选择编号：").strip()
    if not pick.isdigit() or not (1 <= int(pick) <= len(choices)):
        return "你犹豫片刻，决定暂不拜入宗门。"

    target = choices[int(pick) - 1]
    need = 40
    if p.cultivation < need:
        return f"{target} 的门槛是修为 {need}，你目前尚未达标。"

    p.faction = target
    p.reputation += 5
    p.stones += 20
    return f"你成功加入 {target}，获入门资源（灵石 +20，声望 +5）。"


def rest(world: World) -> str:
    p = world.player
    cost = 6
    if p.stones < cost:
        return "灵石不足，无法住店休整。"
    p.stones -= cost
    heal = random.randint(12, 24)
    qi = random.randint(12, 22)
    p.hp = min(p.max_hp, p.hp + heal)
    p.qi = min(p.max_qi, p.qi + qi)
    return f"你在客栈静养一夜，气血 +{heal}，真气 +{qi}（灵石 -{cost}）。"


def show_npc_book(world: World) -> str:
    p = world.player
    known = sorted(p.social.items(), key=lambda kv: kv[1], reverse=True)
    if not known:
        return "你还没有结识稳定的人脉。"
    top = known[:12]
    lines = ["你的人脉簿："]
    for name, favor in top:
        npc = next((n for n in world.npcs if n.name == name and n.alive), None)
        tag = "挚友" if favor >= 30 else "泛泛之交" if favor >= 0 else "宿怨"
        if npc:
            lines.append(f"- {name}：好感 {favor}（{tag}），{npc.role}/{npc.faction}，现居 {npc.location}")
        else:
            lines.append(f"- {name}：好感 {favor}（已失去联系）")
    return "\n".join(lines)


def save_game(world: World) -> str:
    p = world.player
    data = {
        "turn": world.turn,
        "player": {
            "name": p.name,
            "age": p.age,
            "title": p.title,
            "spouse": p.spouse,
            "children": [asdict(c) for c in p.children],
            "clan_name": p.clan_name,
            "clan_prestige": p.clan_prestige,
            "max_hp": p.max_hp,
            "hp": p.hp,
            "max_qi": p.max_qi,
            "qi": p.qi,
            "cultivation": p.cultivation,
            "stones": p.stones,
            "reputation": p.reputation,
            "karma": p.karma,
            "location": p.location,
            "faction": p.faction,
            "inventory": p.inventory,
            "social": p.social,
            "party": p.party,
            "active_quests": [asdict(q) for q in p.active_quests],
            "weapon_bonus": p.weapon_bonus,
            "armor_bonus": p.armor_bonus,
            "weapon_name": p.weapon_name,
            "armor_name": p.armor_name,
            "artifact": p.artifact,
            "artifact_charge": p.artifact_charge,
        },
        "npcs": [asdict(n) for n in world.npcs],
        "log": world.log[-30:],
    }
    SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"存档成功：{SAVE_PATH}"


def load_game() -> World | None:
    if not SAVE_PATH.exists():
        return None
    data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    world = World(data["player"]["name"])
    world.turn = data["turn"]

    p = world.player
    p.age = data["player"]["age"]
    p.title = data["player"].get("title", "无名散修")
    p.spouse = data["player"].get("spouse")
    p.children = [Child(**c) for c in data["player"].get("children", [])]
    p.clan_name = data["player"].get("clan_name", f"{p.name}家")
    p.clan_prestige = data["player"].get("clan_prestige", 0)
    p.max_hp = data["player"].get("max_hp", 120)
    p.hp = data["player"]["hp"]
    p.max_qi = data["player"].get("max_qi", 80)
    p.qi = data["player"].get("qi", 80)
    p.cultivation = data["player"]["cultivation"]
    p.stones = data["player"]["stones"]
    p.reputation = data["player"]["reputation"]
    p.karma = data["player"].get("karma", 0)
    p.location = data["player"]["location"]
    p.faction = data["player"]["faction"]
    p.inventory = data["player"]["inventory"]
    p.social = data["player"]["social"]
    p.party = data["player"].get("party", [])
    p.active_quests = [Quest(**q) for q in data["player"].get("active_quests", [])]
    p.weapon_bonus = data["player"].get("weapon_bonus", 0)
    p.armor_bonus = data["player"].get("armor_bonus", 0)
    p.weapon_name = data["player"].get("weapon_name", "凡铁剑")
    p.armor_name = data["player"].get("armor_name", "布衣")
    p.artifact = data["player"].get("artifact")
    p.artifact_charge = data["player"].get("artifact_charge", 0)

    world.npcs = [NPC(**n) for n in data["npcs"]]
    world.log = data.get("log", [])
    return world


def bootstrap_world() -> World:
    if SAVE_PATH.exists():
        choice = input("检测到存档，是否读取？(y/n): ").strip().lower()
        if choice == "y":
            loaded = load_game()
            if loaded:
                print("已读取存档。")
                return loaded
            print("存档损坏或读取失败，将开始新游戏。")

    name = input("请输入道号：").strip() or "无名散修"
    return World(name)


def main() -> None:
    print("=== 高自由度修仙模拟人生：战斗深化版 ===")
    world = bootstrap_world()

    while True:
        p = world.player
        update_player_title(p)
        if not p.is_alive():
            print("\n你气血耗尽，陨落于修真乱世。")
            break
        if p.cultivation >= 1800:
            print("\n你踏入化神，名震诸域，终得逍遥！")
            break

        print("\n" + "=" * 48)
        print(f"第 {world.turn} 年")
        print(p.summary())
        print("\n【江湖近闻】")
        print(world.show_world_news())
        print("\n行动：")
        print("1. 打坐修炼")
        print("2. 云游四方")
        print("3. 猎妖/战斗历练")
        print("4. 结识与互动 NPC")
        print("5. 使用物品")
        print("6. 加入宗门")
        print("7. 客栈休整")
        print("8. 查看人脉簿")
        print("9. 任务中心")
        print("10. 坊市采购/装备")
        print("11. 家族事务（道侣/子嗣）")
        print("12. 传位给子嗣（继承开局）")
        print("13. 队伍管理（高好感 NPC 入队）")
        print("14. 存档")
        print("15. 结束此生")

        act = input("请选择：").strip()
        if act == "1":
            print(meditate(world))
        elif act == "2":
            print(roam(world))
        elif act == "3":
            print(work_or_hunt(world))
        elif act == "4":
            print(meet_npc(world))
        elif act == "5":
            print(consume_item(world))
        elif act == "6":
            print(join_faction(world))
        elif act == "7":
            print(rest(world))
        elif act == "8":
            print(show_npc_book(world))
            continue
        elif act == "9":
            print(quest_center(world))
        elif act == "10":
            print(market(world))
        elif act == "11":
            print(family_hall(world))
        elif act == "12":
            print(pass_to_heir(world))
        elif act == "13":
            print(manage_party(world))
        elif act == "14":
            print(save_game(world))
            continue
        elif act == "15":
            print("你收剑归鞘，暂别尘世纷争。")
            break
        else:
            print("无效输入，请重试。")
            continue

        world.tick_world()


if __name__ == "__main__":
    main()
