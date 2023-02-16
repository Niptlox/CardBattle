from typing import Dict

CAPABILITY_PUNCH = 2
CAPABILITY_SHOOT = 4
CAPABILITY_PROTECT = 8
CAPABILITY_MAGIC = 16

ITEM_TOOL = 1
ITEM_POISON = 2
ITEM_EAT = 4

EFFECT_INSTANT_HEALTH = 1

S_HEALTH = "health"
S_MANA = "mana"
S_TYPE = "type"
S_TITLE = "title"
S_IMGID = "img_id"
S_ANCESTOR = "ancestor"
S_EFFECT = "effect"
S_RESTORING_HEALTH = "restoring_health"
S_CAPABILITIES = "capabilities"
S_MAX_CELL_CNT = "max_cell_cnt"
S_ENEMY = "enemy"

S_PUNCH_DAMAGE = "punch_damage"
S_PUNCH_DAMAGE_MIN = "punch_damage_min"
S_PUNCH_DAMAGE_MAX = "punch_damage_max"
S_PUNCH_CHANCE = "punch_chance"

Capabilities = {
    "DefaultPunch": {S_TYPE: CAPABILITY_PUNCH, S_TITLE: "Default punch", S_PUNCH_CHANCE: 0.7, S_PUNCH_DAMAGE_MIN: 10,
                     S_PUNCH_DAMAGE_MAX: 15},
    "LightPunch": {S_ANCESTOR: "DefaultPunch", S_TITLE: "Light Punch", S_PUNCH_DAMAGE_MIN: 5, S_PUNCH_DAMAGE_MAX: 7,}
}
Creatures = {
    "BlackCat": {S_TITLE: "ЪУЪ", S_IMGID: 5, S_HEALTH: 50, S_CAPABILITIES: ["DefaultPunch", ], S_ENEMY: True},
    "CryCat": {S_TITLE: "Cry cat", S_IMGID: 6, S_HEALTH: 30, S_CAPABILITIES: ["LightPunch", ], S_ENEMY: True},
}

# Виды ввода эффекта: "id effect"; {S_ANCESTOR: "id effect", }; ("id effect", steps); ("id effect", steps, mul_cof))
Effects = {
    "RestoreHealth": {S_TYPE: EFFECT_INSTANT_HEALTH, S_TITLE: "Восстановление жизни", S_HEALTH: 5}
}

Items = {
    "Poison": {S_TYPE: ITEM_POISON, S_TITLE: "Poison", S_MAX_CELL_CNT: 8},
    "HealthPoison": {S_ANCESTOR: "Poison", S_TITLE: "Health Poison", S_HEALTH: 30},
    "HealthSmallPoison": {S_ANCESTOR: "HealthPoison", S_TITLE: "Health Small Poison", S_HEALTH: 10},
    "HealthBigPoison": {S_ANCESTOR: "HealthPoison", S_TITLE: "Health Big Poison", S_HEALTH: 50},
    "RestoreHealthPoison": {S_ANCESTOR: "Poison", S_TITLE: "Restore Health Poison", S_HEALTH: 10, S_EFFECT: ("RestoreHealth", 5)},
}


def unpack_option(option, options: Dict[str, dict]):
    if option.get(S_ANCESTOR) is None:
        return option
    anc_option = options.get(option.get(S_ANCESTOR)).copy()
    anc_option.update(option)
    return anc_option


def __unpack_options(options):
    options = options.copy()
    for key in options:
        options[key] = unpack_option(options[key], options)
    return options


Capabilities = __unpack_options(Capabilities)
Creatures = __unpack_options(Creatures)
Effects = __unpack_options(Effects)
Items = __unpack_options(Items)