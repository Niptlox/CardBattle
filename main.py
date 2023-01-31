import pygame as pg
import pygame.display
import random

pg.init()

CAPABILITY_PUNCH = 2
CAPABILITY_SHOOT = 4
CAPABILITY_PROTECT = 8
CAPABILITY_MAGIC = 16

S_LIVES = "lives"
S_MANA = "mana"
S_CTYPE = "ctype"
S_TITLE = "title"
S_IMGID = "img_id"

S_PUNCH_DAMAGE = "punch_damage"
S_PUNCH_DAMAGE_MIN = "punch_damage_min"
S_PUNCH_DAMAGE_MAX = "punch_damage_max"
S_PUNCH_CHANCE = "punch_chance"

PLAYER_IMG_ID = 0
imgs = [pygame.image.load(f"sprites/{i}.png") for i in range(7)]

capabilities_options = {
    "DefaultPunch": {S_CTYPE: CAPABILITY_PUNCH, S_TITLE: "Default punch", S_PUNCH_CHANCE: 0.7, S_PUNCH_DAMAGE_MIN: 7,
                     S_PUNCH_DAMAGE_MAX: 12}
}
creature_options = {
    "BlackCat": {S_TITLE: "ЪУЪ", S_IMGID: 5, S_LIVES: 50, "capabilities": ["DefaultPunch", ]},
    "CryCat": {S_TITLE: "Cry cat", S_IMGID: 6, S_LIVES: 30, "capabilities": ["DefaultPunch", ]},
}


def get_creature(creature_id):
    options = creature_options[creature_id]
    return Creature(options, get_capabilities(options["capabilities"]))


def get_capability(cap_id):
    return Capability(capabilities_options.get(cap_id))


def get_capabilities(cap_ids):
    return [get_capability(cap_id) for cap_id in cap_ids]


class Creature:
    def __init__(self, options, capabilities, alive=True):
        self.options = options
        self.name = options[S_TITLE]
        self.img_id = options[S_IMGID]
        self.lives = options[S_LIVES]
        self.mana = options.get(S_MANA, -1)
        self.capabilities = capabilities
        self.alive = alive

    def get_punch(self, damage, capability):
        self.get_damage(damage)

    def get_damage(self, damage):
        self.lives -= damage
        if self.lives <= 0:
            self.kill()

    def kill(self):
        self.alive = False

    def draw(self, surface, pos):
        surface.blit(imgs[self.img_id], pos)


class Button:
    button_font = pg.font.SysFont("Arial", 20, )

    def __init__(self, rect, text, on_click=None, text_color="BLACK", background="WHITE", font=button_font):
        self.rect = pg.Rect(rect)
        self.surface = pg.Surface(self.rect.size)
        self.surface.fill(background)
        self.on_click = on_click
        text_surface = font.render(text, True, text_color)
        self.surface.blit(text_surface, ((self.rect.w - text_surface.get_width()) // 2,
                          (self.rect.h - text_surface.get_height()) // 2))

    def pgevent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                self.click()

    def draw(self, surface):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            surface.blit(self.surface, (self.rect.x, self.rect.y + 2))
        else:
            surface.blit(self.surface, (self.rect.x, self.rect.y))

    def click(self):
        if self.on_click:
            self.on_click()


class Capability:
    def __init__(self, options):
        if options is None:
            raise Exception("Capability init ERROR, variable 'options' is None")
        self.options = options
        self.name = options[S_TITLE]
        self.ctype = options[S_CTYPE]

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


class CapabilityPunch:
    def __init__(self, damage):
        super(CapabilityPunch, self).__init__({S_PUNCH_DAMAGE: damage, S_CTYPE: CAPABILITY_PUNCH,
                                               S_TITLE: "Capability Punch"})


class Player(Creature):
    def __init__(self):
        options = {S_LIVES: 100, S_MANA: 0, S_IMGID: PLAYER_IMG_ID, S_TITLE: "Player"}
        capabilities = get_capabilities(["DefaultPunch"])
        super(Player, self).__init__(options, capabilities, alive=True)


WSIZE = (960, 720)
screen = pygame.display.set_mode(WSIZE)
running = True


def pg_update(ui_objects=None, iterator=False):
    global running
    if ui_objects:
        for obj in ui_objects:
            obj.draw(screen)
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if ui_objects:
            for obj in ui_objects:
                obj.pgevent(event)
        if iterator:
            yield event


font = pg.font.SysFont("Arial", 20)


def battle(player, opponents):
    global battle_running, current, now_opponent

    def punch(_cap, opp):
        global current, battle_running, now_opponent
        _cap.start_action(opp)
        now_opponent += 1
        while now_opponent < len(opponents) and not opponents[now_opponent].alive :
            current += 1
        if now_opponent >= len(opponents):
            now_opponent = 0
            current ^= 1
        if not any([opp.alive for opp in opponents]):
            battle_running = False

    now_opponent = 0
    current = 0
    opponent = opponents[now_opponent]

    battle_running = True
    ui_objects = []
    y = 0
    for cap in player.capabilities:
        ui_objects.append(Button((10, 300 + y, 120, 30), cap.name,
                                 on_click=lambda _cap=cap: punch(_cap, opponent)))
        y += 25
    while running and battle_running:
        screen.fill("black")
        if current == 0:
            # player
            opponents[now_opponent].draw(screen, (30, 30))
        elif current == 1:
            for opp in opponents:
                opp.capabilities[0].start_action(player)
            current = 0
        screen.blit(font.render(f"Player: {player.lives,}", True, "WHITE"), (0, 0))
        if not player.alive:
            battle_running = False
        list(pg_update(ui_objects, iterator=False))


global current, battle_running, now_opponent
player = Player()
opponents = [get_creature("BlackCat"), get_creature("BlackCat"), get_creature("CryCat")]
battle(player, opponents)

while running:
    list(pg_update(iterator=False))
