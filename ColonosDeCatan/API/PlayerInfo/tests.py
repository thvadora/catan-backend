from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.db import transaction, IntegrityError

from django.contrib.auth.models import User

from API.Board.models import Board, Card, Resource
from API.Board.models import Hex, HexPosition, VertexPosition
from API.Games.models import Dice, Game
from API.PlayerInfo.models import Player
from API.Room.models import Room

from API.PlayerInfo.serializers import PlayerSerializer

from API.User.views import CustomAuthToken
from API.PlayerInfo.views import PlayerPersonalInfo

import random


"""Pequeño script automatizada para testing de la info del player"""

# Base de datos
USERS = [
    {"username": "00sb", "password": "kelokeEsto"},
    {"username": "pacoPerfum", "password": "yEstoQes"},
    {"username": "admin", "password": "admin"},
    {"username": "ingenieria", "password": "ingenieria"}
]

CARDS = [
    {"type": "road_building"},
    {"type": "year_of_plenty"},
    {"type": "monopoly"},
    {"type": "victory_point"},
    {"type": "knight"}
]

RESOURCE = [
    {"type": "brick"},
    {"type": "lumber"},
    {"type": "wool"},
    {"type": "grain"},
    {"type": "ore"}
]

COLOURS = [
    {"colour": "Red"},
    {"colour": "Blue"},
    {"colour": "Green"},
    {"colour": "Orange"},
]


class PlayerInfoTest(TestCase):
    @classmethod
    def setUpClass(cls):

        super(PlayerInfoTest, cls).setUpClass()

        # creando el objeto del modelo de usuario en la base de datos.
        for user in USERS:
            new_user = User.objects.create(
                username=user['username'],
                password=user['password']
            )
            new_user.save()
        print('Usuarios agregados: -OK-')

        # creando el objeto del modelo de cartas en la base de datos.
        for card in CARDS:
            new_card = Card.objects.create(
                type=card['type']
            )
            new_card.save()
        print('Cartas agregadas -OK-')

        # creando el objeto del modelo de recursos en la base de datos.
        for resource in RESOURCE:
            new_resource = Resource.objects.create(
                type=resource['type']
            )
            new_resource.save()
            # print('Added resource id:', new_resource.id,
            #      'with type:', new_resource.type)
        print('Recursos agregados: -OK-')

        # creando el objeto del modelo de hexposition en la base de datos.
        HexPosition(level=0, index=0).save()
        for level in range(1, 3):
            for index in range(0, 6 * level):
                hex_position = HexPosition(level=level, index=index)
                hex_position.save()
        print('HexPsosition agregados: -OK-')

        # creando el objeto del modelo de tablero en la base de datos.
        num_board = 1  # number of boards
        hex_positions = HexPosition.objects.all()
        list_hex_positions = list(hex_positions)
        resources = Resource.objects.all()
        list_resources = list(Resource.objects.all())
        list_boards = list(('board' + str(i), i)
                           for i in range(0, num_board))
        for name_board, id_board in list_boards:
            tokens = list(i for i in range(0, 19))
            random.shuffle(tokens)
            board = Board.objects.create(
                name=name_board,
                id=id_board)
            board.save()
            for i in range(0, 19):
                hexagon = Hex.objects.create(
                    terrain=random.choice(list_resources),
                    position=list_hex_positions[i],
                    token=tokens[i])
                hexagon.save()
                board.hexes.add(hexagon)
            board.save()
            print('Tableros agregados -OK-')

        # creando el objeto del modelo de habitaciones en la base de datos.
        users = User.objects.all()
        room = Room.objects.create(
            name='EsteLobby',
            owner=users[2],
            max_players=2)
        room.save()
        print('Rooms agregados: -OK-')

    # test url de user para obtener el token de la base de datos
    def test_User_post(self):
        users = User.objects.all()
        list_users = list(users)
        client = Client()
        for user in list_users:
            response = client.post(
                '/users/login/',
                {'user': user.username,
                 'pass': user.password}).json()
            self.assertTrue('token' in response)
            token = response['token']
            response = client.get(
                '/boards',
                HTTP_AUTHORIZATION='Token {}'.format(
                    token))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data, [])

    # test de creacion de player.
    def test_PlayerPersonalInfo(self):

        users = User.objects.all()
        colours = COLOURS
        min_len = min(len(users), len(colours))

        # creando el objeto del modelo de player en la base de datos.
        for i in range(0, min_len):
            player = Player(username=users[i],
                            colour=colours[i]['colour']
                            )
            player.save()
        print('Players agregados: -OK-')

        players = Player.objects.all()
        rooms = Room.objects.all()
        for room in rooms:
            room.players.add(players[0])
            room.players.add(players[1])
        print('Rooms agregadas: -OK-')

    # test de obtencion de player de la base de datos.
    def test_PlayerPersonalInfo_get(self):
        self.test_PlayerPersonalInfo()
        num_board = 1  # number of boards
        client = Client()
        for i in range(0, num_board):
            dice = Dice(x=0, y=0)
            dice.save()
            robb = VertexPosition(level=0, index=0)
            robb.save()
            user = User(username=str(i), password=str(i))
            user.save()
            cards = list(Card.objects.all())
            reqs = list(Resource.objects.all())
            player = Player.objects.create(
                username=user,
                colour=COLOURS[i]['colour'],
            )
            player.save()
            player.resources.set(reqs)
            player.cards.set(cards)
            player.save()
            game = Game(id=i,
                        in_turn=player,
                        name='game' + str(i),
                        dices=dice,
                        robber=robb,
                        board=Board.objects.get(id=i))
            game.save()
            game.players.add(player)
            game.save()
            print('Juego', game.id, 'agregado con player:',
                  game.in_turn.username, 'en turno')
            games = list(Game.objects.all())
            for game in games:
                user = User.objects.get(username=game.in_turn.username)
                response = client.post(
                    '/users/login/',
                    {'user': user.username,
                     'pass': user.password}).json()
                self.assertTrue('token' in response)
                token = 'Token ' + response['token']
                response = client.get('/games/' + str(game.id) + '/player',
                                      HTTP_AUTHORIZATION=token)
            self.assertEqual(response.status_code, 200)
            print("Cartas y Recursos: -OK-")

    # test para checkear un mala obtencion de player de la base de datos.
    def test_PlayerPersonalInfo_Fail_get(self):
        print("Cartas y Recursos cuando el player no esta en el juego:")
        self.test_PlayerPersonalInfo()
        num_board = 1  # number of boards
        client = Client()
        for i in range(0, num_board):
            dice = Dice(x=0, y=0)
            dice.save()
            robb = VertexPosition(level=0, index=0)
            robb.save()
            user = User(username=str(i), password=str(i))
            user.save()
            cards = list(Card.objects.all())
            reqs = list(Resource.objects.all())
            player = Player.objects.create(
                username=user,
                colour=COLOURS[i]['colour'],
            )
            player.save()
            player.resources.set(reqs)
            player.cards.set(cards)
            player.save()
            game = Game(id=i,
                        in_turn=player,
                        name='game' + str(i),
                        dices=dice,
                        robber=robb,
                        board=Board.objects.get(id=i))
            game.save()
            games = list(Game.objects.all())
            for game in games:
                user = User.objects.get(username=game.in_turn.username)
                response = client.post(
                    '/users/login/',
                    {'user': user.username,
                     'pass': user.password}).json()
                self.assertTrue('token' in response)
                token = 'Token ' + response['token']
                response = client.get('/games/' + str(game.id) + '/player',
                                      HTTP_AUTHORIZATION=token)
            self.assertTrue(response.status_code, 200)
            print("-OK-")

    # test para checkear una mala obtenciín de game.
    def test_PlayerPersonalInfo_FailGame_get(self):
        self.test_PlayerPersonalInfo()
        num_board = 1  # number of boards
        client = Client()
        for i in range(0, num_board):
            dice = Dice(x=0, y=0)
            dice.save()
            robb = VertexPosition(level=0, index=0)
            robb.save()
            user = User(username=str(i), password=str(i))
            user.save()
            cards = list(Card.objects.all())
            reqs = list(Resource.objects.all())
            player = Player.objects.create(
                username=user,
                colour=COLOURS[i]['colour'],
            )
            player.save()
            player.resources.set(reqs)
            player.cards.set(cards)
            player.save()
            game = Game(id=i,
                        in_turn=player,
                        name='game' + str(i),
                        dices=dice,
                        robber=robb,
                        board=Board.objects.get(id=i))
            game.save()
            game.players.add(player)
            game.save()
            print('Juego', game.id, 'agregado con player:',
                  game.in_turn.username, 'en turno')
            games = list(Game.objects.all())
            for game in games:
                user = User.objects.get(username=game.in_turn.username)
                response = client.post(
                    '/users/login/',
                    {'user': user.username,
                     'pass': user.password}).json()
                self.assertTrue('token' in response)
                token = 'Token ' + response['token']
                response = client.get('/games/' +
                                      str(game.id + 100) +
                                      '/player',
                                      HTTP_AUTHORIZATION=token)
            self.assertTrue(response.status_code, 200)
            print("Cartas y Recursos cuando no existe el juego: -OK-")
