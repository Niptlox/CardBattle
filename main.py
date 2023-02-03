import pygame as pg
import pygame.display
import random

pg.init()
WSIZE = (960, 720)
screen = pygame.display.set_mode(WSIZE, flags=pg.SRCALPHA)

CAPABILITY_PUNCH = 2
CAPABILITY_SHOOT = 4
CAPABILITY_PROTECT = 8
CAPABILITY_MAGIC = 16

S_LIVES = "lives"
S_MANA = "mana"
S_CTYPE = "ctype"
S_TITLE = "title"
S_IMGID = "img_id"
S_ANCESTOR = "ancestor"

S_PUNCH_DAMAGE = "punch_damage"
S_PUNCH_DAMAGE_MIN = "punch_damage_min"
S_PUNCH_DAMAGE_MAX = "punch_damage_max"
S_PUNCH_CHANCE = "punch_chance"

PLAYER_IMG_ID = 0
img_size = (220, 220)
imgs = [pygame.image.load(f"sprites/{i}.png") for i in range(7)]
shadow_img = pg.Surface(img_size).convert()
shadow_img.fill("#64748baa")
shadow_img.set_alpha(220)

capabilities_options = {
    "DefaultPunch": {S_CTYPE: CAPABILITY_PUNCH, S_TITLE: "Default punch", S_PUNCH_CHANCE: 0.7, S_PUNCH_DAMAGE_MIN: 10,
                     S_PUNCH_DAMAGE_MAX: 15},
    "LightPunch": {S_ANCESTOR: "DefaultPunch", S_PUNCH_DAMAGE_MIN: 5, S_PUNCH_DAMAGE_MAX: 7, S_TITLE: "Light Punch"}
}
creature_options = {
    "BlackCat": {S_TITLE: "ЪУЪ", S_IMGID: 5, S_LIVES: 50, "capabilities": ["DefaultPunch", ]},
    "CryCat": {S_TITLE: "Cry cat", S_IMGID: 6, S_LIVES: 30, "capabilities": ["LightPunch", ]},
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
        self.max_lives = options[S_LIVES]
        self.lives = self.max_lives
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

    @property
    def lives_percent(self):
        return self.lives / self.max_lives

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
            if event.button == pg.BUTTON_LEFT and self.rect.collidepoint(event.pos):
                self.click()

    def draw(self, surface):
        if self.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            surface.blit(self.surface, (self.rect.x, self.rect.y + 2))
        else:
            surface.blit(self.surface, (self.rect.x, self.rect.y))

    def click(self):
        if self.on_click:
            self.on_click()


class Capability:
    def __init__(self, options: dict):
        if options is None:
            raise Exception("Capability init ERROR, variable 'options' is None")
        self.ancestor = options.get(S_ANCESTOR)
        if self.ancestor:
            self.options = capabilities_options[self.ancestor].copy()
            self.options.update(options)
        else:
            self.options = options
        self.name = self.options[S_TITLE]
        self.ctype = self.options[S_CTYPE]

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
        capabilities = get_capabilities(["DefaultPunch", "LightPunch"])
        super(Player, self).__init__(options, capabilities, alive=True)
        self.battle = None

    def start_battle(self, opponents):
        self.battle = Battle(self, opponents)
        return self.battle


PLAYER = 1
OPPONENT = 2


class Battle:
    def __init__(self, player, opponents):
        self.player = player
        self.opponents = opponents
        self.current_opponent = 0
        # 1 = player; 2 = monster
        self.master = PLAYER
        self.win = 0
        self.running = True

    def player_punch(self, capability):
        if self.master == PLAYER:
            capability.start_action(self.opponents[self.current_opponent])
            self.next_opponent()
            return True

    def opponent_move(self):
        for opp in self.opponents:
            if opp.alive:
                opp.capabilities[0].start_action(self.player)
                if not player.alive:
                    self.win = OPPONENT
                    self.running = False
                    return

        self.master = PLAYER

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
        self.current_opponent = 0
        self.master = OPPONENT


running = True


def pg_update_iter(ui_objects=None):
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
        yield event


def pg_update(ui_objects=None):
    return list(pg_update_iter(ui_objects))


font = pg.font.SysFont("Arial", 20)
font_a1 = pg.font.SysFont("Arial", 40)


def color_of_lives_percent(lives_percent):
    color = "#64ee8b"
    if player.lives_percent < 0.6:
        color = "#fef08a"
    if player.lives_percent < 0.3:
        color = "#ef4444"
    return color


def battle(player: Player, _opponents):
    battle = player.start_battle(_opponents)

    ui_objects = []
    y = 0
    for cap in player.capabilities:
        ui_objects.append(Button((10, 300 + y, 120, 30), cap.name,
                                 on_click=lambda _cap=cap: battle.player_punch(_cap)))
        y += 25 + 10
    while running:

        screen.fill("black")

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
                pg.draw.rect(screen, "#64ee8b", ((x, y + 220 + 2), (220 * opp.lives_percent, 5)))
            else:
                pg.draw.line(screen, "red", (x + 5, y + 5), (x + img_size[0] - 5, y + img_size[1] - 5), 5)
                pg.draw.line(screen, "red", (x + img_size[0] - 5, y + 5), (x + 5, y + img_size[1] - 5), 5)

            if i == battle.current_opponent:
                pg.draw.rect(screen, "white", ((x + 50, y + 220 + 13), (220 - 100, 5)))

            x += 250
            i += 1


        screen.blit(font.render(f"Player: {player.lives}", True, "WHITE"), (0, 0))
        pg.draw.rect(screen, "#64748b", ((5, 25), (300, 8)))
        if player.alive:
            pg.draw.rect(screen, color_of_lives_percent(player.lives_percent),
                         ((5, 25 + 1), (300 * player.lives_percent, 8 - 2)))


        if battle.running:
            if battle.master == OPPONENT:
                battle.opponent_move()
            pg_update(ui_objects)
        else:
            text = font_a1.render("YOU WIN" if battle.win == PLAYER else "YOU DIED", True, "red")
            screen.blit(text, ((WSIZE[0] - text.get_width()) // 2,
                               (WSIZE[1] - text.get_height()) // 2))

            pg_update()


player = Player()
opponents = [get_creature("BlackCat"), get_creature("BlackCat"), get_creature("CryCat")]
battle(player, opponents)

while running:
    pg_update([])
