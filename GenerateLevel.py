import math
import random
from collections import defaultdict

import pygame

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
    connections[0] = []
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
    # new_room_id = cnt_rooms - last_cnt + 1
    new_rooms_params = []
    for next_pos in next_positions:
        new_room_id = get_free_id(connections)
        _flag = 0
        if set_fin:
            _flag = ROOM_FINISH
        connections[room_id].append(new_room_id)
        connections[new_room_id].append(room_id)
        used_positions.add(next_pos)
        new_rooms_params.append(
            (rooms, new_room_id, connections, used_positions, new_last_cnt, cnt_rooms, diffic + 1, next_pos,
             _flag))
    for params in new_rooms_params:
        generate_room(*params)
        # new_room_id += 1


def get_free_id(connections: dict):
    if not connections:
        return 0
    return max(connections.keys()) + 1


class GenLevel:
    def __init__(self, cnt_rooms):
        self.cnt_rooms = cnt_rooms

        self.rooms = []
        self.connections = defaultdict(list)
        self.connections[0] = []
        self.used_positions = set()

    def get_result(self):
        return self.rooms, self.connections


def create_level(cnt_rooms):
    size = int(cnt_rooms ** 0.5) + 3
    print("Size", size)
    rooms = []
    used_positions = set()
    diffic = 0
    flag = 0
    connections = defaultdict(list)
    for room_id in range(cnt_rooms):
        pos = random.randint(0, size), random.randint(0, size)
        while pos in used_positions:
            pos = random.randint(0, size), random.randint(0, size)
        used_positions.add(pos)
        rooms.append([room_id, diffic, pos, flag])

    for room in rooms:
        room_connect = []
        rpos = room[2]
        min_d = 1e9
        rsize = 10
        rooms_rect = [(r[0], pygame.Rect(r[2][0] * rsize, r[2][1] * rsize, rsize, rsize)) for r in rooms]

        for room2 in rooms:
            if room[0] == room2[0]:
                continue
            rpos2 = room2[2]
            d = dist(rpos2, rpos)
            if d < min_d:
                min_d = d
                room_connect = [room2[0]]
            elif d == min_d:
                room_connect.append(room2[0])
        # xy1 =
        # for room2 in rooms:
        #     if room[0] == room2[0] or room2[0] in room_connect:
        #         continue
        #     rpos2 = room2[2]
        #     for rect_id, room_rect in rooms_rect:
        #         if rect_id == room[0] or rect_id == room2[0]:
        #             continue
        #
        #         if room_rect.clipline((x1, y1), (x2, y2)):
        #         print("hit")
        #
        #         room_connect.append(room2[0])

        connections[room[0]] = room_connect
    print(check_group_of_rooms(connections))
    return rooms, connections


def check_group_of_rooms(connections):
    def rec(now, group, connections):
        group.add(now)
        for conn in connections[now]:
            if conn not in group:
                rec(conn, group, connections)
        return group

    groups = []
    all_rooms = set()
    for room_i in connections.keys():
        if room_i not in all_rooms:
            group = rec(room_i, set(), connections)
            groups.append(group)
            all_rooms |= group

    return groups


def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


if __name__ == '__main__':
    print(generate_level(5))
