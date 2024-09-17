import logging
import os
from datetime import datetime
from hearthstone.enums import CardType, Zone, GameTag
from hslog import LogParser, packets
from hslog.export import EntityTreeExporter
from entity.game_entity import GameEntity
from entity.hero_entity import HeroEntity
from entity.spell_entity import SpellEntity

# import entity.cards as ecards

logger = logging.getLogger()


class LogUtil:
    def __init__(self, hs_path):
        self.hs_path = hs_path
        self.parser = LogParser()
        self.game = None
        # parse 完后可直接拿来用
        self.game_entity = None

    # 获取炉石日志，现在要取到最新的文件夹的日志
    def get_hs_log(self, hs_path):
        # 假设 cfg['hs_path'] 已经定义好了
        logs_folder = os.path.join(os.path.dirname(hs_path), 'Logs')

        # 获取 Logs 文件夹下的所有子目录
        sub_dirs = [d for d in os.listdir(logs_folder) if os.path.isdir(os.path.join(logs_folder, d))]

        # 筛选出以日期格式命名的文件夹
        date_sub_dirs = []
        for subdir in sub_dirs:
            try:
                # 尝试将子目录名称转换为 datetime 对象
                # 注意这里的日期格式是 '2024_08_16_17_36_39'
                date_sub_dirs.append((datetime.strptime(subdir[len("Hearthstone_"):], '%Y_%m_%d_%H_%M_%S'), subdir))
            except ValueError:
                # 如果转换失败，则忽略该子目录
                continue

        # 如果没有找到任何日期格式的文件夹，则抛出异常或返回 None
        if not date_sub_dirs:
            raise ValueError("No date-formatted directories found.")

        # 按照日期排序并获取最新的日期
        latest_date, latest_dir = max(date_sub_dirs)

        # 构建完整的文件路径
        return os.path.join(logs_folder, latest_dir, 'Power.log')

    def read_log(self):
        with open(self.get_hs_log(self.hs_path), encoding='utf-8') as f:
            self.parser.read(f)
        self.parser.flush()
        # 最近一场战斗
        packet_tree = self.parser.games[-1]
        exporter = EntityTreeExporter(packet_tree, player_manager=self.parser.player_manager)
        ee = exporter.export()
        self.game = ee.game

    def parse_game(self) -> GameEntity:
        self.read_log()
        for e in self.game.entities:
            # 以下为游戏状态
            if e.type == CardType.GAME:

                # print(e, e.tags, end='\n\n\n')
                # player = e.players
                # for p in player:
                #     print(p.tags, end='\n\n')
                self.game_entity = GameEntity(e)
                pass
            elif e.type == CardType.MINION:
                minion = HeroEntity(e)
                # print(e, e.tags, end='\n\n\n')
                self.game_entity.add_hero(minion)
                pass
            # 佣兵技能信息
            elif e.type == CardType.LETTUCE_ABILITY:
                # print(e, e.tags, end='\n\n\n')
                owner = e.tags.get(GameTag.LETTUCE_ABILITY_OWNER)
                # print(e.card_id)
                if owner in self.game_entity.hero_entities.keys():
                    # hcid = self.game_entity.hero_entities[owner].card_id[:-3]
                    # cid = e.card_id[:-3]
                    # cname = 'ecards.' + hcid + '.' + cid + '.' + cid + '(e)'
                    # print(cname)
                    # try:
                    #     spell_entity = eval(cname)
                    # except Exception as ex:
                    #     logger.warning(ex)
                    spell_entity = SpellEntity(e)
                    # spell_entity = SpellEntity(e)
                    self.game_entity.hero_entities[owner].add_spell(spell_entity)
                pass
            # 对战技能记录
            elif e.type == CardType.SPELL:
                # print(e, e.tags, end='\n\n\n')
                pass

        # for h in self.game_entity.my_hero:
        #     if h.card_id[:-3] not in HEROS.keys():
        #         continue
        #     hd = HEROS[h.card_id[:-3]]
        #     for i, s in enumerate(h.spell):
        #         if i > 2:
        #             break
        #         s.read_from_config(hd[3][i])

        return self.game_entity

    pass


if __name__ == '__main__':
    path = "C:/var/Hearthstone/"
    hs_log = LogUtil(path)
    game_entity = hs_log.parse_game()
    for i in game_entity.my_hero:
        print(i)

    for i in game_entity.enemy_hero:
        print(i)

    pass
