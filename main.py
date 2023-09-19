from typing import List

import pygame as pg
import pygame.display
import random

from pygame import Vector2

from GenerateLevel import ROOM_START, ROOM_FINISH, generate_level, create_level
from data import *

pg.init()
WSIZE = (960, 720)
screen = pygame.display.set_mode(WSIZE, flags=pg.SRCALPHA)

PLAYER_IMG_ID = 0
img_size = (220, 220)
imgs = [pygame.image.load(f"{i}.png") for i in range(7)]
shadow_img = pg.Surface(img_size).convert()
shadow_img.fill("#64748baa")
shadow_img.set_alpha(220)

SCN_WORLD = 0
SCN_BATTLE = 1
SCN_MAPLEVEL = 2
scene = SCN_MAPLEVEL


def set_scene(scene_id):
    global scene
    scene = scene_id


def get_creature(creature_id):
    options = Creatures[creature_id]
    return Creature(options, get_capabilities(options["capabilities"]))


def get_creatures(creature_ids):
    return [get_creature(cr_id) for cr_id in creature_ids]


def random_creatures_from_list(init_lst, difficult=0):
    max_diff_offset = max([abs(Creatures[cr_id][S_DIFFICULT] - difficult) for cr_id, cnt in init_lst]) * 2
    get_chance = lambda cr_id: max_diff_offset / (max_diff_offset - abs(Creatures[cr_id][S_DIFFICULT] - difficult))
    unpack_list = [cr_id for cr_id, cnt in init_lst for _ in range(cnt)]
    chances = [get_chance(cr_id) for cr_id, cnt in init_lst for _ in range(cnt)]
    creatures = random.choices(unpack_list, chances)
    return creatures


def get_capability(cap_id):
    return Capability(Capabilities.get(cap_id))


def get_capabilities(cap_ids):
    return [get_capability(cap_id) for cap_id in cap_ids]


class Creature:
    def __init__(self, options, capabilities, alive=True):
        self.options = options
        self.name = options[S_TITLE]
        self.img_id = options[S_IMGID]
        self.max_health = options.get(S_HEALTH, -1)
        self.enemy = options.get(S_ENEMY, False)
        self.health = self.max_health
        self.mana = options.get(S_MANA, -1)
        self.capabilities = capabilities
        self.alive = alive

    def get_punch(self, damage, capability):
        self.get_damage(damage)

    def get_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def add_health(self, health):
        self.health = min(self.max_health, self.health + health)
        if self.health <= 0:
            self.kill()

    def kill(self):
        self.alive = False

    @property
    def health_percent(self):
        return self.health / self.max_health

    def draw(self, surface, pos):
        surface.blit(imgs[self.img_id], pos)


class Label:
    _font = pg.font.SysFont("Arial", 20, )

    def __init__(self, rect, text, text_color="BLACK", background="WHITE", font=_font):
        self.rect = pg.Rect(rect)
        self.font = font
        self.background = background
        self.text_color = text_color
        self.surface = pg.Surface(self.rect.size)
        self.set_text(text)
        self.enable = True

    def set_text(self, text):
        self.surface.fill(self.background)
        text_surface = self.font.render(text, True, self.text_color)
        self.surface.blit(text_surface, ((self.rect.w - text_surface.get_width()) // 2,
                                         (self.rect.h - text_surface.get_height()) // 2))

    def pg_event(self, event):
        pass

    def draw(self, surface):
        surface.blit(self.surface, (self.rect.x, self.rect.y))

    def set_enable(self, enable):
        self.enable = enable


class Button(Label):
    _font = pg.font.SysFont("Arial", 20, )

    def __init__(self, rect, text, on_click=None, text_color="BLACK", background="WHITE", font=_font):
        super(Button, self).__init__(rect, text, text_color, background, font)
        self.on_click = on_click

    def pg_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT and self.rect.collidepoint(event.pos):
                self.click()

    def draw(self, surface):
        if self.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            surface.blit(self.surface, (self.rect.x, self.rect.y + 2))
        else:
            surface.blit(self.surface, (self.rect.x, self.rect.y))

    def click(self):
        if self.on_click:
            self.on_click(self)


class Capability:
    def __init__(self, options: dict):
        if options is None:
            raise Exception("Capability init ERROR, variable 'options' is None")
        self.ancestor = options.get(S_ANCESTOR)
        if self.ancestor:
            self.options = Capabilities[self.ancestor].copy()
            self.options.update(options)
        else:
            self.options = options
        self.name = self.options[S_TITLE]
        self.ctype = self.options[S_TYPE]

    def punch(self, other: Creature):
        damage = self.options.get(S_PUNCH_DAMAGE, -1)
        if damage == -1:
            damage = random.randint(self.options.get(S_PUNCH_DAMAGE_MIN, 0), self.options.get(S_PUNCH_DAMAGE_MAX, 0))
        chance = self.options.get(S_PUNCH_CHANCE, 1)
        if random.random() <= chance:
            other.get_punch(damage, self)
            print(other, damage)

    def start_action(self, other):
        if self.ctype is CAPABILITY_PUNCH:
            self.punch(other)


# class CapabilityPunch:
#     def __init__(self, damage):
#         super(CapabilityPunch, self).__init__({S_PUNCH_DAMAGE: damage, S_TYPE: CAPABILITY_PUNCH,
#                                                S_TITLE: "Capability Punch"})
class Inventory:
    def __init__(self, size=10):
        self.size = size
        self._lst = [None] * self.size

    @property
    def list(self):
        return self._lst

    def __getitem__(self, item):
        return self._lst.__getitem__(item)

    def add_item(self, item, cnt=1) -> int:
        """Положить предметы. Возаращает сколько не вместилось"""
        max_cnt = Items[item].get(S_MAX_CELL_CNT)
        for i in range(self.size):
            if self._lst[i] is None:
                self._lst[i] = [item, 0]
            if self._lst[i][0] == item:
                cell_cnt = self._lst[i][1]
                free = max_cnt - cell_cnt
                if cnt > free:
                    self._lst[i] = [item, max_cnt]
                    cnt -= free
                else:
                    self._lst[i] = [item, cell_cnt + cnt]
                    cnt = 0
            if cnt == 0:
                return 0
        return cnt

    def add_items(self, items):
        """Положить список предметов"""
        for item, cnt in items:
            lost = self.add_item(item, cnt, )

    def get_item(self, item, cnt=1) -> 0:
        """Забрать преедметы. Возаращает сколько не хватило"""
        for i in range(self.size):
            if self._lst[i] is not None and self._lst[i][0] == item:
                if self._lst[i][1] > cnt:
                    self._lst[i][1] -= cnt
                    cnt = 0
                else:
                    cnt -= self._lst[i][1]
                    self._lst[i] = None
                if cnt == 0:
                    return 0
        return cnt

    def get_cnt_of_cell(self, cell_index, cnt=1):
        """Взять кол-во из определенной ячейки. Возаращает сколько не хватило"""
        if self._lst[cell_index] is not None:
            self._lst[cell_index][1] -= cnt
            if self._lst[cell_index][1] <= 0:
                lost = -self._lst[cell_index][1]
                self._lst[cell_index] = None
                return lost
        return


class Player(Creature):
    def __init__(self):
        options = {S_HEALTH: 100, S_MANA: 0, S_IMGID: PLAYER_IMG_ID, S_TITLE: "Player"}
        capabilities = get_capabilities(["DefaultPunch", "LightPunch"])
        super(Player, self).__init__(options, capabilities, alive=True)
        self.battle: Battle = None
        self.inventory = Inventory(size=10)
        self.inventory.add_items([("HealthPoison", 3), ("RestoreHealthPoison", 1)])
        self.coins = 0
        self.effects = []
        self.room: Room = None
        self.map_level: MapLevel = None

    def start_battle(self, opponents):
        """Стартовать битву с оппонентами"""
        self.battle = Battle(self, opponents)
        return self.battle

    def apply_item(self, cell_index):
        item, cnt = self.inventory[cell_index]
        prop = Items.get(item)
        if prop[S_TYPE] == ITEM_POISON:
            if prop.get(S_HEALTH):
                self.add_health(prop.get(S_HEALTH))
            self.inventory.get_cnt_of_cell(cell_index)

    def enter_room(self, room):
        self.room = room
        if room.check_enemy():
            self.battle = Battle(self, room.get_enemy())

    def leave_room(self):
        if self.battle and self.battle.running:
            return False
        self.room = None
        return True


PLAYER = 1
OPPONENT = 2


class Battle:
    def __init__(self, player: Player, opponents: List[Creature]):
        self.player = player
        self.opponents = opponents
        self.current_opponent = 0
        # 1 = player; 2 = monster
        self.master = PLAYER
        self.win = 0
        self.running = True
        self.in_room = True

    def player_punch(self, capability):
        if self.master == PLAYER:
            capability.start_action(self.opponents[self.current_opponent])
            self.next_opponent()
            return True

    def player_apply_item(self, cell_index):
        self.player.apply_item(cell_index)

    def opponent_move(self):
        for opp in self.opponents:
            if opp.alive:
                opp.capabilities[0].start_action(self.player)
                if not player.alive:
                    self.win = OPPONENT
                    self.running = False
                    return

        self.master = PLAYER
        self.next_opponent()

    def next_opponent(self):
        # след опонент когда ходит игрок
        while self.current_opponent < (len(self.opponents) - 1):
            self.current_opponent += 1
            if self.opponents[self.current_opponent].alive:
                return self.opponents[self.current_opponent]
        if not any([opp.alive for opp in opponents]):
            self.running = False
            self.win = PLAYER
            return
        self.current_opponent = -1
        self.master = OPPONENT

    def exit_at_room(self):
        self.in_room = False


class Room:
    def __init__(self, creatures, position=(0, 0), flag=0, difficult=0, auto_generate=False, room_id=-1):
        self.creatures = creatures
        self.position = position
        self.flag = flag
        self.difficult = difficult
        self.room_id = room_id
        if auto_generate:
            self.generate(difficult)

    def generate(self, difficult=0):
        self.difficult = difficult
        self.creatures = []
        if self.flag & ROOM_START:
            return
        if self.flag & ROOM_FINISH:
            return
        if 1 <= difficult <= 4:
            crts = [("BlackCat", difficult + 1)]
        else:
            crts = []
        creatures_ids = random_creatures_from_list(crts, difficult)
        self.creatures = get_creatures(creatures_ids)

    def get_enemy(self):
        return [crt for crt in self.creatures if crt.enemy]

    def check_enemy(self):
        return self.get_enemy()

    @property
    def is_start(self):
        return self.flag & ROOM_START

    @property
    def is_finish(self):
        return self.flag & ROOM_FINISH

    def __str__(self):
        return f"Room<#{self.room_id}; {self.position}; {self.creatures}>"

    def __repr__(self):
        return self.__str__()


class MapLevel:
    def __init__(self, difficult=0, auto_generate=False):
        self.rooms = []
        self.connections = []
        self.difficult = difficult
        if auto_generate:
            self.generate(self.difficult)

    def generate(self, difficult=0):
        self.difficult = difficult
        space = 1
        self.rooms = []
        if difficult == 0:
            return
        cnt_rooms = 5 + difficult + random.randint(int(difficult ** 0.2), int(difficult ** 0.5))
        g_rooms, self.connections = create_level(cnt_rooms)
        for g_room in g_rooms:
            room_id, dif_room, pos, flag = g_room
            pos = pos[0] * space, pos[1] * space
            self.rooms.append(Room([], pos, flag=ROOM_START, difficult=dif_room, auto_generate=True, room_id=room_id))


running = True


def pg_update_iter(ui_objects=None):
    global running
    if ui_objects:
        for obj in ui_objects:
            if obj.enable: obj.draw(screen)
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if ui_objects:
            for obj in ui_objects:
                if obj.enable: obj.pg_event(event)
        yield event


def pg_update(ui_objects=None):
    return list(pg_update_iter(ui_objects))


font = pg.font.SysFont("Arial", 20)
font_a1 = pg.font.SysFont("Arial", 40)


def color_of_health_percent(health_percent):
    color = "#64ee8b"
    if player.health_percent < 0.6:
        color = "#fef08a"
    if player.health_percent < 0.3:
        color = "#ef4444"
    return color


def scene_battle(battle):
    set_scene(SCN_BATTLE)
    player = battle.player
    end_ui = []
    end_label = Label(((WSIZE[0] - 200) // 2, (WSIZE[1] - 40) // 2, 200, 40), "", background="black", text_color="red",
                      font=font_a1)
    end_ui.append(end_label)
    end_ui.append(Button(((WSIZE[0] - 200) // 2, (WSIZE[1] - 40) // 2 + 50, 200, 40), "Выйти из комнаты",
                         on_click=lambda _b: set_scene(SCN_WORLD)))
    ui_objects = []
    ui_objects.append(Label((10, 310, 220, 30), "Способности", text_color="white", background="black"))
    ui_objects.append(Label((610, 310, 220, 30), "Инвентарь", text_color="white", background="black"))
    y = 350
    for cap in player.capabilities:
        ui_objects.append(Button((10, y, 220, 30), cap.name,
                                 on_click=lambda _b, _cap=cap: battle.player_punch(_cap)))
        y += 25 + 10

    while running and scene == SCN_BATTLE:

        screen.fill("black")

        fast_ui = []

        # player
        x, y = 30, 50
        i = 0
        for opp in battle.opponents:
            opp.draw(screen, (x, y))

            text_surface = font.render(opp.name, True, "white", "black")
            screen.blit(text_surface, (x + (img_size[0] - text_surface.get_width()) // 2,
                                       y + 3))

            pg.draw.rect(screen, "#64748b", ((x, y + 220 + 2), (220, 5)))
            if opp.alive:
                pg.draw.rect(screen, "#64ee8b", ((x, y + 220 + 2), (220 * opp.health_percent, 5)))
            else:
                pg.draw.line(screen, "red", (x + 5, y + 5), (x + img_size[0] - 5, y + img_size[1] - 5), 5)
                pg.draw.line(screen, "red", (x + img_size[0] - 5, y + 5), (x + 5, y + img_size[1] - 5), 5)

            if i == battle.current_opponent:
                pg.draw.rect(screen, "white", ((x + 50, y + 220 + 13), (220 - 100, 5)))

            x += 250
            i += 1

        screen.blit(font.render(f"Player: {player.health}HP", True, "WHITE"), (0, 0))
        pg.draw.rect(screen, "#64748b", ((5, 25), (300, 8)))
        if player.alive:
            pg.draw.rect(screen, color_of_health_percent(player.health_percent),
                         ((5, 25 + 1), (300 * player.health_percent, 8 - 2)))

        if battle.running:

            y = 350
            for i in range(player.inventory.size):
                if player.inventory[i] is not None:
                    item, cnt = player.inventory[i]
                    fast_ui.append(Button((610, y, 220, 30), Items[item].get(S_TITLE) + f" ({cnt})",
                                          on_click=lambda _b, _i=i: battle.player_apply_item(_i)))
                y += 25 + 10

            if battle.master == OPPONENT:
                battle.opponent_move()
            pg_update(ui_objects + fast_ui)
        else:
            end_label.set_text("YOU WIN" if battle.win == PLAYER else "YOU DIED")
            pg_update(end_ui)


font = pg.font.SysFont("arial", 15)


def scene_maplevel(map_level):
    set_scene(SCN_MAPLEVEL)
    ui_objects = []
    rooms = map_level.rooms
    offset_x, offset_y = WSIZE[0] // 2, WSIZE[1] // 2
    print(offset_x, offset_y)
    cof_scale = 50
    room_size = cof_scale // 3 * 2
    convert_room_pos = lambda _room: (offset_x + _room.position[0] * cof_scale,
                                      offset_y + _room.position[1] * cof_scale)
    room_id1 = 0
    print(map_level.connections)
    print(rooms)
    while running and scene == SCN_MAPLEVEL:
        screen.fill("black")
        pg.draw.circle(screen, "red", (offset_x, offset_y), 10)
        c = 30

        # for room_id1 in map_level.connections:

        if 1:
            for room_id1 in map_level.connections:
                for room_id2 in map_level.connections[room_id1]:
                    color = (c, c, c)
                    c += 5
                    pos1 = Vector2(convert_room_pos(rooms[room_id1])) + Vector2(room_size) // 2
                    pos2 = Vector2(convert_room_pos(rooms[room_id2])) + Vector2(room_size) // 2
                    # print(room_id1, room_id2, pos1, pos2, rooms[room_id1].position, rooms[room_id2].position)
                    pg.draw.line(screen, color, pos1, pos2, 4)

        for room in rooms:
            pg.draw.rect(screen, "white", (convert_room_pos(room), (room_size, room_size)))
            screen.blit(font.render(str(room.difficult)+";"+str(room.room_id), True, "black"), convert_room_pos(room))
        # print(map_level.rooms)
        # print(map_level.connections)

        for event in pg_update_iter(ui_objects):
            # print(event)
            if event.type == pg.KEYDOWN:
                room_id1 += 1
                room_id1 = room_id1 % len(map_level.connections)
                print(room_id1, map_level.connections[room_id1])
                if event.key == pg.K_ESCAPE:
                    set_scene(SCN_BATTLE)


        # pg_update(ui_objects)
    # break


player = Player()
while 1:
    map_level = MapLevel(1, True)
    print(map_level.rooms)
    scene_maplevel(map_level)

opponents = [get_creature("BlackCat"), get_creature("BlackCat"), get_creature("CryCat")]
room = Room(opponents)
player.enter_room(room)

scene_battle(player.battle)
# scene_world(None)
while running:
    pg_update([])