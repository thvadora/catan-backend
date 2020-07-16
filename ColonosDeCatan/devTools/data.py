from API.Board.models import *
from API.Games.models import *
from API.PlayerInfo.models import *
from API.User.models import *
from API.Room.models import *
from API.Transaction.models import *
from devTools.all import deleteALL
import random
import requests
import json

RESOURCE = ["brick", "lumber", "wool", "grain", "ore"]
CARDS = [
    "knight",
    "monopoly",
    "road_building",
    "year_of_plenty",
    "victory_point",
]
BOARD = [("L", 1), ("Z", 2)]
USER = ["0", "1", "2", "3"]


def new_resources_list(ls=RESOURCE):
    rlist = []
    for x in ls:
        r = Resource(type=x)
        r.save()
        rlist.append(r)
    return rlist


def new_cards_list(ls=CARDS):
    rlist = []
    for x in ls:
        r = Card(type=x)
        r.save()
        rlist.append(r)
    return rlist


def add_hex_pos():
    HexPosition(level=0, index=0).save()
    for x in range(1, 3):
        for y in range(0, 6 * x):
            hp = HexPosition(level=x, index=y)
            hp.save()


def add_board():
    if len(list(HexPosition.objects.all())) == 0:
        add_hex_pos()
    lh = list(HexPosition.objects.all())
    lr = new_resources_list()
    for N, ID in BOARD:
        ls = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 2, 3, 4, 5, 6, 8, 9, 10, 11]
        random.shuffle(ls)
        b = Board(name=N, id=ID)
        b.save()
        k = random.randint(0, len(ls))
        for i in range(0, len(ls)):
            if i == k:
                r = Resource(type='desert')
                r.save()
            else:
                r = random.choice(lr)
                r.save()
            hex = Hex(terrain=r, position=lh[i], token=ls[i])
            hex.save()
            b.hexes.add(hex)
        b.save()


def add_user():
    for n in USER:
        user = User(username=n, password=n)
        user.save()


def add_dice():
    dice = Dice(x=random.randint(1, 6), y=random.randint(1, 6))
    dice.save()


def add_vertexP(b):
    ls = (0, 0)
    for x in b.hexes.all():
        if x.terrain.type == "desert":
            ls = (x.position.level, x.position.index)
    vp = VertexPosition(level=ls[0], index=ls[1])
    vp.save()
    return vp


def add_player():
    if len(list(User.objects.all())) is 0:
        add_user()
    ls = (User.objects.all())
    for x in ls:
        p = Player(username=x, colour='blue')
        p.save()
        for i in range(4):
            new_resources = new_resources_list()
            for r in new_resources:
                p.resources.add(r)
        lc = new_cards_list()
        for x in lc:
            p.cards.add(x)
        if p.username.username == "3":
            p.resources.all().delete()
            p.cards.all().delete()
        p.save()


def f(model):
    return (model.objects.first())


def add_deck(game):
    for i in range(0, 25):
        if i < 14:
            c = Card(type="knight")
            c.save()
        elif i < 16:
            c = Card(type="monopoly")
            c.save()
        elif i < 18:
            c = Card(type="road_building")
            c.save()
        elif i < 20:
            c = Card(type="year_of_plenty")
            c.save()
        else:
            c = Card(type="victory_point")
            c.save()
        game.deck.add(c)
    game.save()


def add_game():
    if len(list(Dice.objects.all())) is 0:
        add_dice()
    if len(list(User.objects.all())) is 0:
        add_user()
    if len(list(Board.objects.all())) is 0:
        add_board()
    if len(list(Player.objects.all())) is 0:
        add_player()
    b = f(Board)
    game = Game(name="game1",
                id=0,
                in_turn=Player.objects.get(
                    username=User.objects.get(username="0")),
                dices=f(Dice),
                robber=add_vertexP(b),
                board=b)
    game.save()
    add_deck(game)
    for x in Player.objects.all():
        game.players.add(x)
    game.save()


def add_rooms():
    colours = ['Red', 'Green', 'Yellow', 'Blue']
    lp = []
    for i in range(4, 8):
        u = User(username=str(i), password=str(i))
        u.save()
        if i == 4:
            us = u
        p = Player(username=u, colour=colours[(i - 4)])
        p.save()
        ls = new_resources_list()
        for x in ls:
            p.resources.add(x)
        p.save()
        lp.append(p)

    room = Room(name="room1",
                id=1,
                max_players=4,
                owner=us)
    room.save()
    for x in lp:
        room.players.add(x)

    room.board = Board.objects.get(id=2)
    room.save()


# Pongo casas para fede en (0,0) y (1,3)
def add_hause(name, pos):
    game = Game.objects.get(name='game1')
    p = game.players.get(username=User.objects.get(username=name))
    h = VertexPosition(level=pos[0], index=pos[1])
    h.save()
    p.settlements.add(h)
    p.save()


def add_houses(name='0', pos=[[1, 2], [1, 3]]):
    for x in pos:
        add_hause(name, x)


def add_road(name='0', pos=[[0, 0], [1, 3]]):
    game = Game.objects.get(name='game1')
    p = game.players.get(username=User.objects.get(username=name))

    vp0 = VertexPosition(level=pos[0][0], index=pos[0][1])
    vp1 = VertexPosition(level=pos[1][0], index=pos[1][1])
    vp0.save()
    vp1.save()
    rd = RoadPosition(x=vp0, y=vp1)
    rd.save()
    p.roads.add(rd)
    p.save()


def more_resources(name="0", res=RESOURCE):
    user = User.objects.get(username=name)
    game = Game.objects.get(name='game1')
    player = game.players.get(username=user)
    rl = new_resources_list(res)
    for r in rl:
        player.resources.add(r)
    player.save()


def more_cards(name="0", res=CARDS):
    user = User.objects.get(username=name)
    game = Game.objects.get(name='game1')
    player = game.players.get(username=user)
    rl = new_cards_list(res)
    for r in rl:
        player.cards.add(r)
    player.save()


def set_turn(name):
    u = User.objects.get(username=name)
    p = Player.objects.get(username=u)
    g = Game.objects.get(id=0)
    g.in_turn = p
    g.save()


def set_dice7():
    user = Game.objects.get(id=0).in_turn.username.username
    url = "http://127.0.0.1:8000/users/login/"
    data = {'user': user, 'pass': user}

    res = requests.request("POST", url, data=data)
    t = "Token " + res.json()['token']

    url = "http://127.0.0.1:8000/games/0/player/actions"
    urlgame = "http://127.0.0.1:8000/games/0"
    payload = {
        'type': 'end_turn',
        'payload': ''
    }
    headers = {
        'Authorization': t,
    }
    while(True):
        response = requests.request("POST", url, data=payload, headers=headers)
        data = response.json()
        res = requests.request("GET", urlgame, headers=headers).json()['dices']
        if res[0] + res[1] == 7:
            break


def main():
    deleteALL()
    add_game()
    add_rooms()
    add_houses()
    add_hause(name='2', pos=[1, 11])
    add_road(pos=[[0, 0], [1, 0]])
