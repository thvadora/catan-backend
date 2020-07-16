from API.PlayerInfo.models import Player
from API.PlayerInfo.serializers import PlayerSerializer
from API.Board.models import *
from API.Room.models import Room
from API.Room.serializers import RoomSerializer
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
import random


RESOURCE = ["brick", "lumber", "wool", "grain", "ore", "desert"]

# test room


class RoomTest(TestCase):
    def add_resource(self):
        for res in RESOURCE:
            r = Resource(type=res)
            r.save()

    def add_hex_pos(self):
        HexPosition(level=0, index=0).save()
        for lv in range(1, 3):
            for ind in range(0, 6 * lv):
                hp = HexPosition(level=lv, index=ind)
                hp.save()

    def add_board(self, n=3):
        if len(list(Resource.objects.all())) == 0:
            self.add_resource()
        if len(list(HexPosition.objects.all())) == 0:
            self.add_hex_pos()
        BOARD = list(('board' + str(i), i) for i in range(0, n))
        lh = list(HexPosition.objects.all())
        lr = list(Resource.objects.all())
        for Name, ID in BOARD:
            tokens = list(i for i in range(0, 19))
            random.shuffle(tokens)
            b = Board(name=Name, id=ID)
            b.save()
            for i in range(0, 19):
                hex = Hex(terrain=random.choice(lr),
                          position=lh[i],
                          token=tokens[i])
                hex.save()
                b.hexes.add(hex)
            b.save()

    def setUp(self):
        user = User(username='a', password='a')
        user.save()
        player = Player(username=user, colour='red')
        player.save()
        user = User(username='b', password='b')
        user.save()
        player = Player(username=user, colour='blue')
        player.save()
        user = User(username='c', password='c')
        user.save()
        player = Player(username=user, colour='green')
        player.save()
        self.add_board()
        board = Board.objects.get(id=0)
        room = Room(id=1, name='ahah', board=board,
                    owner=user, max_players=2)
        room.save()

    def test_create(self):
        print('Testeando POST a /rooms/...')
        client = Client()
        userB = User.objects.get(username='b')
        data = {'user': userB.username, 'pass': userB.password}
        request = client.post('/users/login/', data,
                              content_type='application/json').json()
        USERBTOKEN = 'Token ' + request['token']
        self.add_board()
        # Test sin campo name.
        request = client.post('/rooms/',
                              {'board_id': 1},
                              HTTP_AUTHORIZATION=USERBTOKEN,
                              content_type='application/json')
        self.assertEqual(request.status_code, 400)
        # Test sin campo board_id
        request = client.post('/rooms/',
                              {'name': 'haha'},
                              HTTP_AUTHORIZATION=USERBTOKEN,
                              content_type='application/json')
        self.assertEqual(request.status_code, 400)
        # Test con board_id inexistente
        request = client.post('/rooms/',
                              {'name': 'nuevaRoom',
                               'board_id': 9},
                              HTTP_AUTHORIZATION=USERBTOKEN,
                              content_type='application/json')
        self.assertEqual(request.status_code, 400)
        # Test OK
        request = client.post('/rooms/',
                              {'name': 'Cool Name',
                               'board_id': 1},
                              HTTP_AUTHORIZATION=USERBTOKEN,
                              content_type='application/json')
        self.assertEqual(request.status_code, 200)
        room = Room.objects.get(name='Cool Name')
        serializer = RoomSerializer(room)
        self.assertEqual(serializer.data['name'], 'Cool Name')
        self.assertEqual(serializer.data['owner'], 'b')
        self.assertEqual(serializer.data['max_players'], 4)
        print('-OK!-')

    def test_add_player(self):
        print('Testeando agregado de jugador a una Room particular...')
        user = User.objects.get(username='c')
        player = Player.objects.get(username=user)
        room = Room.objects.get(id=1)
        room.players.add(player)
        serializer = RoomSerializer(room)
        self.assertEqual(serializer.data['id'], 1)
        self.assertEqual(serializer.data['name'], 'ahah')
        self.assertEqual(serializer.data['owner'], 'c')
        self.assertEqual(serializer.data['max_players'], 2)
        self.assertEqual(
            serializer.data['players'][0], 'c')
        print('-OK!-')

    def test_stress(self):
        print('Estresando el modelo Room:',
              'Agregando multiples veces jugadores...')
        for x in range(0, 1000):
            user = User.objects.get(username='a')
            player = Player.objects.get(username=user)
            room = Room.objects.get(id=1)
            room.players.add(player)
            serializer = RoomSerializer(room)
            self.assertEqual(serializer.data['id'], 1)
            self.assertEqual(serializer.data['name'], 'ahah')
            self.assertEqual(serializer.data['owner'], 'c')
            self.assertEqual(serializer.data['max_players'], 2)
            self.assertEqual(serializer.data['players'][0], 'a')
        print('-OK!-')


# test views


class TestView(TestCase):
    def add_resource(self):
        for res in RESOURCE:
            r = Resource(type=res)
            r.save()

    def add_hex_pos(self):
        HexPosition(level=0, index=0).save()
        for lv in range(1, 3):
            for ind in range(0, 6 * lv):
                hp = HexPosition(level=lv, index=ind)
                hp.save()

    def add_board(self, n=3):
        if len(list(Resource.objects.all())) == 0:
            self.add_resource()
        if len(list(HexPosition.objects.all())) == 0:
            self.add_hex_pos()
        BOARD = list(('board' + str(i), i) for i in range(0, n))
        lh = list(HexPosition.objects.all())
        lr = list(Resource.objects.all())
        for Name, ID in BOARD:
            tokens = list(i for i in range(0, 19))
            random.shuffle(tokens)
            b = Board(name=Name, id=ID)
            b.save()
            for i in range(0, 19):
                hex = Hex(terrain=random.choice(lr),
                          position=lh[i],
                          token=tokens[i])
                hex.save()
                b.hexes.add(hex)
            b.save()

    def setUp(self):
        c = Client()
        user = User(username='a', password='a')
        user.save()
        data = {'user': 'a', 'pass': 'a'}
        request = c.post('/users/login/', data,
                         content_type='application/json').json()
        global USER0TOKEN
        USER0TOKEN = 'Token ' + request['token']
        user = User(username='b', password='b')
        user.save()
        data = {'user': 'b', 'pass': 'b'}
        request = c.post('/users/login/', data,
                         content_type='application/json').json()
        global USER1TOKEN
        USER1TOKEN = 'Token ' + request['token']
        user = User(username='c', password='c')
        user.save()
        data = {'user': 'c', 'pass': 'c'}
        request = c.post('/users/login/', data,
                         content_type='application/json').json()
        global USER2TOKEN
        USER2TOKEN = 'Token ' + request['token']
        user = User(username='d', password='d')
        user.save()
        data = {'user': 'd', 'pass': 'd'}
        request = c.post('/users/login/', data,
                         content_type='application/json').json()
        global USER3TOKEN
        USER3TOKEN = 'Token ' + request['token']

    def test_emptyList(self):
        print('Testeando GET a /rooms/...')
        c = Client()
        request = c.get('/rooms/', HTTP_AUTHORIZATION=USER0TOKEN,
                        content_type='application/json')
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data, [])
        print('-OK!-')

    def test_Put(self):
        print('Testeando PUT a /rooms/<id>...')
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        room = Room(name="Cool Name", owner=user, max_players=2)
        room.save()
        c = Client()
        request = c.put('/rooms/1/', HTTP_AUTHORIZATION=USER0TOKEN,
                        content_type='application/json')
        self.assertEqual(request.status_code, 200)
        request = c.get('/rooms/', HTTP_AUTHORIZATION=USER0TOKEN,
                        content_type='application/json')
        self.assertEqual(request.status_code, 200)
        request = request.json()
        self.assertEqual(len(list(request[0]['players'])), 1)
        print('-OK!-')

    def test_stress(self):
        print('Estresando server...')
        r = Room.objects.all().delete()
        for x in range(0, 1000):
            user = User.objects.get(username='a')
            player = Player(id=1, username=user, colour='green')
            player.save()
            room = Room(id=1, name="Cool Name", owner=user, max_players=2)
            room.save()
            c = Client()
            request = c.put('/rooms/1/', HTTP_AUTHORIZATION=USER0TOKEN,
                            content_type='application/json')
            self.assertEqual(request.status_code, 200)
            request = c.get('/rooms/', HTTP_AUTHORIZATION=USER0TOKEN,
                            content_type='application/json')
            self.assertEqual(request.status_code, 200)
            request = request.json()
            self.assertEqual(len(list(request[0]['players'])), 1)
        print('-OK!-')

    def test_addMorePermited(self):
        print('Testeando el agregado de jugadores:',
              'Cuando la Room esta llena...')
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        room = Room(id=2, name="Cool Name", owner=user, max_players=2)
        room.save()
        c = Client()
        tokenlist = [USER0TOKEN, USER1TOKEN, USER2TOKEN]
        for username in range(0, 2):
            if username < 3:
                request = c.put(
                    '/rooms/2/',
                    HTTP_AUTHORIZATION=tokenlist[username],
                    content_type='application/json')
                self.assertEqual(request.status_code, 200)
            else:
                request = c.put(
                    '/rooms/2/',
                    HTTP_AUTHORIZATION=tokenlist[username],
                    content_type='application/json')
                self.assertEqual(request.status_code, 400)
        print('-OK!-')

    def test_getParticularsRooms(self):
        print('Testeando GET a /rooms/<id>/...')
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        room = Room(id=1, name="Cool Name", owner=user, max_players=2)
        room.save()
        c = Client()
        request = c.get('/rooms/1/', HTTP_AUTHORIZATION=USER0TOKEN,
                        content_type='application/json')
        self.assertEqual(request.status_code, 200)
        request = request.json()
        self.assertEqual(request['name'], "Cool Name")
        request = c.get('/rooms/45/', HTTP_AUTHORIZATION=USER0TOKEN,
                        content_type='application/json')
        self.assertEqual(request.status_code, 400)
        print('-OK!-')

    def test_IniciarRoom(self):
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        self.add_board()
        board = Board.objects.get(id=0)
        room = Room(
            id=1,
            name="Room Test",
            owner=user,
            max_players=4,
            board=board)
        room.players.add(player)
        room.save()
        user = User.objects.get(username='b')
        player = Player(username=user, colour='blue')
        player.save()
        room.players.add(player)
        room.save()
        user = User.objects.get(username='c')
        player = Player(username=user, colour='yellow')
        player.save()
        room.players.add(player)
        room.save()
        user = User.objects.get(username='d')
        player = Player(username=user, colour='white')
        player.save()
        room.players.add(player)
        room.save()
        c = Client()

        print('Testeando iniciar partida')
        request = c.patch(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 200)
        print('OK')

    def test_IniciarPartidaNoOwner(self):
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        self.add_board()
        board = Board.objects.get(id=0)
        room = Room(
            id=1,
            name="Room Test",
            owner=user,
            max_players=4,
            board=board)
        room.players.add(player)
        room.save()
        user = User.objects.get(username='b')
        player = Player(username=user, colour='blue')
        player.save()
        room.players.add(player)
        room.save()
        user = User.objects.get(username='c')
        player = Player(username=user, colour='yellow')
        player.save()
        room.players.add(player)
        room.save()
        user = User.objects.get(username='d')
        player = Player(username=user, colour='white')
        player.save()
        room.players.add(player)
        room.save()
        c = Client()

        print('Testeando que no te deje iniciar partida si no es el dueño')
        request = c.patch(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER1TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = c.patch(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER2TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = c.patch(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER3TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        print('OK')

    def test_IniciarPartida_menosde4(self):
        user = User.objects.get(username='a')
        player = Player(username=user, colour='green')
        player.save()
        self.add_board()
        board = Board.objects.get(id=0)
        room = Room(
            id=1,
            name="Room Test",
            owner=user,
            max_players=4,
            board=board)
        room.players.add(player)
        room.save()
        user = User.objects.get(username='b')
        player = Player(username=user, colour='blue')
        player.save()
        room.players.add(player)
        room.save()
        user = User.objects.get(username='c')
        player = Player(username=user, colour='yellow')
        player.save()
        room.players.add(player)
        room.save()

        c = Client()

        print('Testeando iniciar partida con menos jugadores')
        request = c.patch(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        print('OK')


class TestsEliminarRoom(TestCase):
    def setUp(self):
        self.c = Client()
        user = User(username='a', password='a')
        user.save()
        data = {'user': 'a', 'pass': 'a'}
        request = self.c.post('/users/login/', data,
                              content_type='application/json').json()
        global USER0TOKEN
        USER0TOKEN = 'Token ' + request['token']
        user = User(username='b', password='b')
        user.save()
        data = {'user': 'b', 'pass': 'b'}
        request = self.c.post('/users/login/', data,
                              content_type='application/json').json()
        global USER1TOKEN
        USER1TOKEN = 'Token ' + request['token']
        user = User(username='c', password='c')
        user.save()
        data = {'user': 'c', 'pass': 'c'}
        request = self.c.post('/users/login/', data,
                              content_type='application/json').json()
        global USER2TOKEN
        USER2TOKEN = 'Token ' + request['token']
        user = User(username='d', password='d')
        user.save()
        data = {'user': 'd', 'pass': 'd'}
        request = self.c.post('/users/login/', data,
                              content_type='application/json').json()
        global USER3TOKEN
        USER3TOKEN = 'Token ' + request['token']
        self.user1 = User.objects.get(username='a')
        self.user2 = User.objects.get(username='b')
        self.user3 = User.objects.get(username='c')
        self.user4 = User.objects.get(username='d')
        self.player1 = Player(username=self.user1, colour='green')
        self.player1.save()
        self.player2 = Player(username=self.user2, colour='green')
        self.player2.save()
        self.player3 = Player(username=self.user3, colour='green')
        self.player3.save()
        self.player4 = Player(username=self.user4, colour='green')
        self.player4.save()
        self.room = Room(
            id=1,
            name="Cool Name",
            owner=self.user1,
            max_players=4)
        self.room.save()
        self.room.players.add(self.player1)
        self.room.players.add(self.player2)
        self.room.players.add(self.player3)
        self.room.players.add(self.player4)

    def test_BorrarRoom(self):
        print('Testeando DELETE a /rooms/<id>/',
              'tratando de borrar una room con 4 jugadores',
              'siendo el owner de la misma.')
        request = self.c.delete(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 200)
        request = request.json()
        self.assertEqual(request['OK'], "Room eliminada")
        print('OK')
        print('Testeando volver a hacer DELETE a la room recien eliminada...',
              'Asegurandose de que efectivamente se haya borrado.')
        request = self.c.delete(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(request['error'], "No existe Lobby con id: 1")
        print('OK')

    def test_BorrarRoomSinSerOwner(self):
        print('Testeando DELETE a /rooms/<id>/',
              'tratando de borrar una room sin ser el owner de la misma.')
        request = self.c.delete(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER1TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 401)
        request = request.json()
        self.assertEqual(
            request['error'],
            "Sólo el dueño puede eliminar la partida")
        print('OK')

    def test_BorrarRoomInexistente(self):
        print(
            'Testeando DELETE a /rooms/<id>/',
            'tratando de borrar una room',
            'sin que exista una room con ese id.')
        request = self.c.delete(
            '/rooms/25/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(request['error'], "No existe Lobby con id: 25")
        print('OK')

    def test_BorrarPartidaComenzada(self):
        print('Testeando DELETE a /rooms/<id>/',
              'tratando de borrar una room cuyo game ya comenzó')
        self.room.game_has_started = True
        self.room.save()
        request = self.c.delete(
            '/rooms/1/',
            HTTP_AUTHORIZATION=USER0TOKEN,
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(
            request['error'],
            "No se puede borrar una partida ya comenzada")
        print('OK')
