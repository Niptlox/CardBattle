import random

ROOM_START = 1
ROOM_FINISH = 2
ROOM_SHOP = 4


def generate_level(cnt_rooms):
    # Room = (diffic, pos, flag)
    rooms = []
    connections = []
    used_positions = set()


def generate_room(rooms, connections, used_positions, last_cnt, diffic, pos, flag):
    rooms.apped((diffic, pos, flag))
    used_positions.add(pos)
    x, y = pos
    next_positions = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
    next_positions = random.choices(next_positions, k=min(random.randint(1, 4), last_cnt))
    # TODO: доделать
    cnt = last_cnt
    last_cnt = last_cnt - len(next_positions)
    for next_pos in next_positions:
        if next_pos not in used_positions:
            generate_room(rooms, connections, used_positions, last_cnt, diffic+1, next_pos, flag)
