import tempfile
import unittest
from pathlib import Path

import game


class GameTests(unittest.TestCase):
    def test_generate_enemy_returns_positive_stats(self):
        player = game.Player("测试")
        enemy = game.generate_enemy(player, "天火山")
        self.assertGreater(enemy.hp, 0)
        self.assertGreater(enemy.attack, 0)
        self.assertGreaterEqual(enemy.level, 1)
        self.assertTrue(enemy.biography)
        self.assertTrue(enemy.temperament)

    def test_title_progression_by_clan_prestige(self):
        player = game.Player("测试")
        player.clan_prestige = 85
        game.update_player_title(player)
        self.assertEqual(player.title, "一族之主")

    def test_family_tick_grows_children(self):
        world = game.World("测试")
        world.player.children = [game.Child(name="小玄", age=11, talent=70)]
        old = world.player.clan_prestige
        world._family_tick()
        self.assertEqual(world.player.children[0].age, 12)
        self.assertGreaterEqual(world.player.clan_prestige, old)

    def test_save_load_roundtrip_family_fields(self):
        with tempfile.TemporaryDirectory() as td:
            old_save = game.SAVE_PATH
            game.SAVE_PATH = Path(td) / "savegame.json"
            try:
                world = game.World("测试")
                world.player.spouse = "李青"
                world.player.children = [game.Child(name="小雪", age=2, talent=88, destiny="灵根上品")]
                world.player.clan_name = "测试家"
                world.player.clan_prestige = 30
                world.player.artifact = "青莲灯"
                world.player.artifact_charge = 2
                game.save_game(world)
                loaded = game.load_game()
                self.assertIsNotNone(loaded)
                assert loaded is not None
                self.assertEqual(loaded.player.spouse, "李青")
                self.assertEqual(loaded.player.children[0].name, "小雪")
                self.assertEqual(loaded.player.clan_name, "测试家")
                self.assertEqual(loaded.player.clan_prestige, 30)
                self.assertEqual(loaded.player.artifact, "青莲灯")
                self.assertEqual(loaded.player.artifact_charge, 2)
            finally:
                game.SAVE_PATH = old_save

    def test_pass_to_heir_changes_player_identity(self):
        world = game.World("老祖")
        world.player.children = [game.Child(name="少主", age=18, talent=90, destiny="剑心通明")]
        # mock input choose first child
        import builtins
        orig = builtins.input
        builtins.input = lambda prompt="": "1"
        try:
            msg = game.pass_to_heir(world)
        finally:
            builtins.input = orig
        self.assertIn("少主", msg)
        self.assertEqual(world.player.name, "少主")
        self.assertGreaterEqual(world.player.cultivation, 60)

    def test_artifact_can_deal_damage(self):
        player = game.Player("测试")
        player.artifact = "玄雷印"
        player.artifact_charge = 1
        enemy = game.generate_enemy(player, "灵溪谷")
        before = enemy.hp
        dmg, guard, _ = game.use_artifact_in_battle(player, enemy)
        self.assertGreater(dmg, 0)
        self.assertEqual(guard, 0)
        self.assertLess(before - dmg, before)
        self.assertEqual(player.artifact_charge, 0)

    def test_auto_companions_selected_by_relationship(self):
        world = game.World("测试")
        here = world.npcs_here()
        if len(here) < 2:
            self.skipTest("not enough NPCs at same location")
        world.player.social[here[0].name] = 30
        world.player.social[here[1].name] = 28
        companions = game.get_auto_companions(world)
        self.assertGreaterEqual(len(companions), 1)

    def test_party_members_preferred_as_companions(self):
        world = game.World("测试")
        here = world.npcs_here()
        if not here:
            self.skipTest("no npc here")
        world.player.party = [here[0].name]
        companions = game.get_auto_companions(world)
        self.assertTrue(companions)
        self.assertEqual(companions[0].name, here[0].name)


if __name__ == "__main__":
    unittest.main()
