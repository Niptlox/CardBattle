import random
from collections import defaultdict

ROOM_START = 1
ROOM_FINISH = 2
ROOM_SHOP = 4


class LevelGenerator:
    def __init__(self, cnt_rooms):
        self.rooms = []
        self.connections = []
        self.used_positions = set()
        # self.generate_room(cnt_rooms, 1, (0, 0), ROOM_START)


def generate_level(cnt_rooms):
    # Room = (diffic, pos, flag)
    rooms = []
    connections = defaultdict(list)
    used_positions = set()
    generate_room(rooms, 0, connections, used_positions, cnt_rooms, cnt_rooms, 1, (0, 0), ROOM_START)
    return rooms, connections


def generate_room(rooms, room_id, connections, used_positions: set, last_cnt, cnt_rooms, diffic, pos, flag):
    rooms.append((room_id, diffic, pos, flag))
    used_positions.add(pos)
    x, y = pos
    next_positions = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
    next_positions = random.choices(next_positions, k=min(random.randint(1, 4), last_cnt))
    next_positions = [next_pos for next_pos in next_positions if next_pos not in used_positions]
    new_last_cnt = last_cnt - len(next_positions)
    # флаг о том что надо установить финальную комнату
    set_fin = last_cnt == 0
    new_room_id = cnt_rooms - last_cnt + 1
    for next_pos in next_positions:
        _flag = 0
        if set_fin:
            _flag = ROOM_FINISH
        generate_room(rooms, new_room_id, connections, used_positions, new_last_cnt, cnt_rooms, diffic + 1, next_pos,
                      _flag)
        connections[room_id].append(new_room_id)
        connections[new_room_id].append(room_id)
        new_room_id += 1


if __name__ == '__main__':
    print(generate_level(5))
