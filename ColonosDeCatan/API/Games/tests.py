from django.test import TestCase, Client
from API.Board.models import *
from API.Games.models import *
from API.PlayerInfo.models import Player
from API.User.models import User
from API.Games.functions import DistributeResources, GetVertexs
from API.Board.serializers import *
from API.PlayerInfo.serializers import PlayerSerializer, PlayerInfoSerializer
from API.User.serializers import UserSerializer
from rest_framework.renderers import JSONRenderer
import random
import json

RESOURCE = ["brick", "lumber", "wool", "grain", "ore"]


class FillDatabase():
    def __init__(self):
        self.credentials = {}
        self.game = None

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
                          token=tokens[i] % 11 + 2)
                hex.save()
                b.hexes.add(hex)
            b.save()

    def add_game(self, n=3):
        self.add_board(n)
        for i in range(0, n):
            dice = Dice(x=0, y=0)
            dice.save()
            robb = VertexPosition(level=0, index=0)
            robb.save()
            user = User(username=str(i), id=1000 + i)
            user.save()
            player = Player(username=user, colour='Blue')
            player.save()
            game = Game(id=i,
                        in_turn=player,
                        name='game' + str(i),
                        dices=dice,
                        robber=robb,
                        board=Board.objects.get(id=i))
            game.save()
            if i is 1:
                game.players.add(self.player)
                game.save()

    def add_user_player(self):
        if not User.objects.filter(username=self.credentials['user']).exists():
            user = User(username=self.credentials['user'],
                        password=self.credentials['pass'])
            user.save()
            self.player = Player(username=user, colour='Blue')
            self.player.save()

    def add_resource_to_plater(self):
        r = Resource(type='brick')
        r.save()
        self.player.resources.add(r)
        r = Resource(type='lumber')
        r.save()
        self.player.resources.add(r)
        self.player.save()

    def add_card_to_player(self):
        p = self.player
        c = Card(type="knight")
        c.save()
        p.cards.add(c)
        c = Card(type="monopoly")
        c.save()
        p.cards.add(c)
        c = Card(type="road_building")
        c.save()
        p.cards.add(c)
        c = Card(type="year_of_plenty")
        c.save()
        p.cards.add(c)
        c = Card(type="victory_point")
        c.save()
        p.cards.add(c)
        p.save()

    def add_deck(self):
        for i in range(0, 25):
            if i < 14:
                c = Card(type="knight")
                c.save()
                self.game.deck.add(c)
            elif i < 16:
                c = Card(type="monopoly")
                c.save()
                self.game.deck.add(c)
            elif i < 18:
                c = Card(type="road_building")
                c.save()
                self.game.deck.add(c)
            elif i < 20:
                c = Card(type="year_of_plenty")
                c.save()
                self.game.deck.add(c)
            else:
                c = Card(type="victory_point")
                c.save()
                self.game.deck.add(c)

    def add_ver_and_road(self, p):
        v0 = VertexPosition(level=0, index=0)
        v1 = VertexPosition(level=0, index=1)
        v2 = VertexPosition(level=2, index=27)
        v3 = VertexPosition(level=2, index=14)
        v0.save()
        v1.save()
        v2.save()
        v3.save()
        rd = RoadPosition(x=v0, y=v1)
        rd.save()
        p.roads.add(rd)
        p.settlements.add(v2)
        p.cities.add(v3)
        p.save()


class BoardTest(TestCase, FillDatabase):
    def setUp(self):
        self.credentials = {
            'user': 'usuario',
            'pass': 'usuario123'}
        self.add_user_player()
        res = self.client.post('/users/login/',
                               self.credentials,
                               folow=True).json()
        self.token = 'Token ' + res['token']

    def test_obtener_game(self):
        self.add_game(1)
        res = self.client.get('/games/0/board',
                              HTTP_AUTHORIZATION=self.token)
        game = BoardStatusSerializer(Board.objects.get(id=0)).data
        game = json.loads(JSONRenderer().render(game))
        self.assertDictEqual(res.json(), game)
        Game.objects.all().delete()
        Board.objects.all().delete()
        Player.objects.all().delete()
        print('Juego existente -OK-')

    def test_id_invalido(self):
        res = self.client.get('/games/100/board',
                              HTTP_AUTHORIZATION=self.token).json()
        self.assertTrue('Error' in res)
        self.assertEqual(res['Error'],
                         'No se encontro un juego con id = 100')
        print('Juego inexistente -OK-')

    def test_stress(self):
        print('Estresando servidor.')
        n = 100
        self.add_game(100)
        for i in range(0, n):
            res = self.client.get('/games/' + str(i) + '/board',
                                  HTTP_AUTHORIZATION=self.token)
            game = BoardStatusSerializer(Board.objects.get(id=i)).data
            game = json.loads(JSONRenderer().render(game))
            self.assertDictEqual(res.json(), game)
        Game.objects.all().delete()
        Board.objects.all().delete()
        Player.objects.all().delete()
        print('Test estresante superado -OK-')


class BuyCard_RollDices_EndTurn_Test(TestCase, FillDatabase):
    def setUp(self):
        c = Client()
        user1 = User(username='jugador1', password='passdeJugador1')
        user1.save()
        user2 = User(username='jugador2', password='passdeJugador2')
        user2.save()
        user3 = User(username='jugador3', password='passdeJugador3')
        user3.save()
        user4 = User(username='jugador4', password='passdeJugador4')
        user4.save()
        data1 = {'user': 'jugador1', 'pass': 'passdeJugador1'}
        data2 = {'user': 'jugador2', 'pass': 'passdeJugador2'}
        data3 = {'user': 'jugador3', 'pass': 'passdeJugador3'}
        data4 = {'user': 'jugador4', 'pass': 'passdeJugador4'}
        request = c.post(
            '/users/login/',
            data1,
            content_type='application/json').json()
        self.token1 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data2,
            content_type='application/json').json()
        self.token2 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data3,
            content_type='application/json').json()
        self.token3 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data4,
            content_type='application/json').json()
        self.token4 = 'Token ' + request['token']
        self.player1 = Player(id=1, username=user1, colour='Blue')
        self.player1.save()
        self.player2 = Player(id=2, username=user2, colour='Red')
        self.player2.save()
        self.player3 = Player(id=3, username=user3, colour='Green')
        self.player3.save()
        self.player4 = Player(id=4, username=user4, colour='Orange')
        self.player4.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=1,
                         in_turn=self.player1,
                         name='Alto Juego',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.players.add(self.player2)
        self.game.players.add(self.player3)
        self.game.save()

    def test_no_game(self):
        print('Testeando no existencia de juego...')
        c = Client()
        request = c.post(
            '/games/2/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'buy_card',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No se encontro un juego con id = 2')
        request = c.post(
            '/games/4/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'end_turn',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No se encontro un juego con id = 4')
        print('-OK-')

    def test_no_player(self):
        print('Testeando jugador no esta en el juego...')
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'buy_card',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No eres jugador de este juego')
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'end_turn',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No eres jugador de este juego')
        print('-OK-')

    def test_no_turn(self):
        print('No es mi turno...')
        game = Game.objects.get(id=1)
        game.in_turn = self.player2
        game.save()
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token3,
            data={
                'type': 'buy_card',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No es tu turno')
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token3,
            data={
                'type': 'end_turn',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No es tu turno')
        print('-OK-')

    def test_no_resources(self):
        print('No tiene los recursos suficientes...')
        game = Game.objects.get(id=1)
        game.in_turn = self.player3
        game.save()
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token3,
            data={
                'type': 'buy_card',
                'payload': ''}, content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No tienes los recursos suficientes')
        print('-OK-')

    def test_ok(self):
        print('Testeo valido')
        game = Game.objects.get(id=1)
        game.players.add(self.player1)
        game.players.add(self.player2)
        game.players.add(self.player3)
        game.players.add(self.player4)
        game.save()
        r = Resource(type='grain')
        r.save()
        self.player3.resources.add(r)
        r = Resource(type='wool')
        r.save()
        self.player3.resources.add(r)
        r = Resource(type='ore')
        r.save()
        self.player3.resources.add(r)
        self.player3.resources_cards = len(self.player3.resources.all())
        self.player3.save()
        game.in_turn = self.player3
        for i in range(0, 25):
            if i < 14:
                c = Card(type="knight")
                c.save()
                self.game.deck.add(c)
            elif i < 16:
                c = Card(type="monopoly")
                c.save()
                self.game.deck.add(c)
            elif i < 18:
                c = Card(type="road_building")
                c.save()
                self.game.deck.add(c)
            elif i < 20:
                c = Card(type="year_of_plenty")
                c.save()
                self.game.deck.add(c)
            else:
                c = Card(type="victory_point")
                c.save()
                self.game.deck.add(c)
        game.save()
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token3,
            data={
                'type': 'buy_card',
                'payload': ''}, content_type='application/json')
        print(request.data)
        self.assertEqual(200, request.status_code)
        for i in range(0, 3):
            for resource in RESOURCE:
                r = Resource(type=resource)
                r.save()
                self.player3.resources.add(r)
        self.player3.resources_cards = len(self.player3.resources.all())
        self.player3.save()
        for i in range(0, 2):
            for resource in RESOURCE:
                r = Resource(type=resource)
                r.save()
                self.player4.resources.add(r)
        self.player4.resources_cards = len(self.player4.resources.all())
        self.player4.save()
        for resource in RESOURCE:
            r = Resource(type=resource)
            r.save()
            self.player1.resources.add(r)
        self.player1.resources_cards = len(self.player1.resources.all())
        self.player1.save()
        for resource in RESOURCE:
            r = Resource(type=resource)
            r.save()
            self.player2.resources.add(r)
        self.player2.resources_cards = len(self.player2.resources.all())
        self.player2.save()
        game.in_turn = self.player1
        game.turn_number = 9
        game.save()
        c = Client()
        TOKENS = [self.token1, self.token2, self.token3, self.token4]
        list_size = len(TOKENS)
        numberIndex = 0
        while (1):
            game = Game.objects.get(id=1)
            if (game.dices.x + game.dices.y == 7):
                break
            authToken = TOKENS[(numberIndex) % list_size]
            numberIndex = numberIndex + 1
            request = c.post(
                '/games/1/player/actions',
                HTTP_AUTHORIZATION=authToken,
                data={
                    'type': 'end_turn',
                    'payload': ''}, content_type='application/json')
        play1 = PlayerSerializer(list(game.players.all())[0]).data
        play2 = PlayerSerializer(list(game.players.all())[1]).data
        play3 = PlayerSerializer(list(game.players.all())[2]).data
        play4 = PlayerSerializer(list(game.players.all())[3]).data
        play01 = PlayerInfoSerializer(list(game.players.all())[0]).data
        play02 = PlayerInfoSerializer(list(game.players.all())[1]).data
        play03 = PlayerInfoSerializer(list(game.players.all())[2]).data
        play04 = PlayerInfoSerializer(list(game.players.all())[3]).data
        self.assertEqual(len(play01['resources']),
                         play1['resources_cards'])
        self.assertEqual(len(play02['resources']),
                         play2['resources_cards'])
        self.assertEqual(len(play03['resources']),
                         play3['resources_cards'])
        self.assertEqual(len(play04['resources']),
                         play4['resources_cards'])
        self.assertEqual(200, request.status_code)
        print('-OK-')

    def test_roll_dice(self):
        print('Testeando tirada de Dados...')
        c = Client()
        game = Game.objects.get(id=1)
        game.players.add(self.player4)
        game.in_turn = self.player4
        game.turn_number = 9
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token4,
            data={
                'type': 'end_turn',
                'payload': ''}, content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = c.get(
            '/games/1',
            HTTP_AUTHORIZATION=self.token4, content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertGreaterEqual(request['current_turn']['dice'][0], 1)
        self.assertGreaterEqual(request['current_turn']['dice'][1], 1)
        print('-OK-')


class WinGame_Test(TestCase, FillDatabase):
    def setUp(self):
        c = Client()
        user1 = User(username='jugador1', password='passdeJugador1')
        user1.save()
        data1 = {'user': 'jugador1', 'pass': 'passdeJugador1'}
        request = c.post(
            '/users/login/',
            data1,
            content_type='application/json').json()
        self.token1 = 'Token ' + request['token']
        self.player1 = Player(id=1, username=user1, colour='Blue')
        self.player1.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=999,
                         in_turn=self.player1,
                         name='Alto Juego',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.players.add(self.player1)
        self.game.save()

    def test_win_game(self):
        print('Testeando Ganar Partida')
        c = Client()
        self.game = Game.objects.get(id=999)
        self.game.turn_number = 9
        self.game.save()
        self.player1.points = 10
        self.player1.save()
        self.assertEqual(self.game.winner, None)
        request = c.post(
            '/games/999/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'end_turn',
                'payload': ''}, content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.game = Game.objects.get(id=999)
        self.assertEqual(self.game.winner, self.player1)
        print('-OK-')


class BankTradeTest(TestCase, FillDatabase):
    def setUp(self):
        c = Client()
        user = User(username='a', password='a')
        user.save()
        data = {'user': 'a', 'pass': 'a'}
        request = c.post(
            '/users/login/',
            data,
            content_type='application/json').json()
        self.token = 'Token ' + request['token']
        self.player = Player(id=1, username=user, colour='Blue')
        self.player.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=1,
                         in_turn=self.player,
                         name='Alto Juego',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.save()

    def test_bank_trade_no_res(self):
        game = Game.objects.get(id=1)
        game.players.add(self.player)
        game.in_turn = self.player
        game.save()
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'bank_trade',
                'payload': '{\'give\':"ore", \'receive\':"wool"}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No tienes los recursos suficientes')
        print('Error al intercambiar con el banco sin recursos : OK')

    def test_bank_trade_no_turn(self):
        user = User(username='b', password='b')
        user.save()
        player = Player(username=user, colour='red')
        player.save()
        game = Game.objects.get(id=1)
        game.players.add(self.player)
        game.in_turn = player
        game.save()
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'bank_trade',
                'payload': '{\'give\':"ore", \'receive\':"wool"}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No es tu turno')
        print('Error al intento de intercambio con el banco no en turno: OK')

    def test_bank_trade(self):
        game = Game.objects.get(id=1)
        game.players.add(self.player)
        game.in_turn = self.player
        game.save()
        for x in range(0, 4):
            ore = Resource(type="ore")
            ore.save()
            self.player.resources.add(ore)
            self.player.save()
        self.player.resources_cards = self.player.resources.all().count()
        self.player.save()
        antes = self.player.resources_cards
        c = Client()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'bank_trade',
                'payload': '{\'give\':"ore", \'receive\':"wool"}'},
            content_type='application/json')
        game = Game.objects.get(id=1)
        player = list(game.players.all())[0]
        self.assertEqual(200, request.status_code)
        self.assertEqual(antes - 3, player.resources_cards)
        print('Intercambiar con el banco: OK')


class TestConstruirPueblo(TestCase, FillDatabase):
    def setUp(self):
        self.credentials = {
            'user': 'usuario',
            'pass': 'usuario123'}
        self.add_user_player()
        res = self.client.post('/users/login/',
                               self.credentials,
                               folow=True).json()
        self.token = 'Token ' + res['token']
        self.add_game()
        self.add_resource()
        vp1 = VertexPosition(level=0, index=0)
        vp1.save()
        vp2 = VertexPosition(level=0, index=1)
        vp2.save()
        rp = RoadPosition(x=vp1, y=vp2)
        rp.save()
        self.player.roads.add(rp)
        self.player.save()
        self.g = Game.objects.get(id=1)
        self.g.players.add(self.player)
        self.g.in_turn = self.player
        for x in RESOURCE:
            r = Resource(type=x)
            r.save()
            self.player.resources.add(r)
        self.player.save()
        self.g.save()
        self.c = Client()

    def test_colocacion_exitosa(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        print('Colocación exitosa de pueblo : OK')

    def test_recursos_invalidos(self):
        self.player.resources.clear()
        self.player.save()
        self.g.turn_number = 9
        self.g.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No tienes los recursos suficientes')
        print('Test de recursos inválidos : OK')

    def test_pueblo_mismo_lugar(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'Ya hay un pueblo construido en esa posición')
        print('Test de colocación de pueblo en el mismo lugar : OK')

    def test_distancia_1(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':1}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No se puede construir pueblo en el vertice deseado.')
        print('Test colocación de pueblo a distancia 1 : OK')

    def test_distancia_2(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':2, \'index\':27}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        print('Test colocación de pueblo a distancia 2 : OK')

    def test_no_en_turno(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        u = User(username='hola', password='jaja123')
        u.save()
        new_player = Player(username=u)
        new_player.save()
        self.g.players.add(new_player)
        self.g.in_turn = new_player
        self.g.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        request = request.json()
        self.assertEqual(request['Error'],
                         'No es tu turno')
        print('Test jugador no en turno : OK')

    def test_camino_valido(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        self.g.turn_number = 40
        self.g.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        print('Test camino valido : OK')

    def test_camino_valido_pero_cerca(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        self.g.turn_number = 40
        self.g.save()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':1}'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)

        request = request.json()
        self.assertEqual(request['Error'],
                         'No se puede construir pueblo en el vertice deseado.')
        print('Test camino válido pero cerca : OK')

    def test_camino_valido_longitud_2(self):
        for x in Resource.objects.all():
            self.player.resources.add(x)
        self.player.save()
        self.g.turn_number = 40
        self.g.save()
        vp1 = VertexPosition(level=0, index=1)
        vp1.save()
        vp2 = VertexPosition(level=1, index=3)
        vp2.save()
        rp = RoadPosition(x=vp1, y=vp2)
        rp.save()
        self.player.roads.add(rp)
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':0, \'index\':0}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_settlement',
                'payload': '{\'level\':1, \'index\':3}'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        request = request.json()
        self.assertEqual(request['OK'],
                         'Pueblo creado.')
        print('Test camino válido de longitud 2: OK')


class TestConstruirCamino(TestCase, FillDatabase):
    def setUp(self):
        self.credentials = {
            'user': 'usuario',
            'pass': 'usuario123'}
        self.add_user_player()
        res = self.client.post('/users/login/',
                               self.credentials,
                               folow=True).json()
        self.token = 'Token ' + res['token']
        self.add_game()
        self.g = Game.objects.get(id=0)
        self.g.players.add(self.player)
        self.g.in_turn = self.player
        self.player.save()
        self.g.save()
        self.c = Client()

    def test_camino_con_camino(self):
        self.add_resource_to_plater()
        self.add_ver_and_road(self.player)
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':0, \'index\':0},\
                             {\'level\':1, \'index\':0}]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Camino construido')
        print('Camino con camino -OK-')

    def test_camino_con_asentamiento(self):
        self.add_resource_to_plater()
        self.add_ver_and_road(self.player)
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':2, \'index\':27},\
                             {\'level\':2, \'index\':28}]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Camino construido')
        print('Camino con asentamiento -OK-')

    def test_camino_con_ciudad(self):
        self.add_resource_to_plater()
        self.add_ver_and_road(self.player)
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':2, \'index\':15},\
                             {\'level\':2, \'index\':14}]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Camino construido')
        print('Camino con ciudad -OK-')

    def test_recursos_insufisientes(self):
        self.add_ver_and_road(self.player)
        self.g.turn_number = 9
        self.g.save()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':2, \'index\':15},\
                             {\'level\':2, \'index\':14}]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'No tienes los recursos suficientes')
        print('Recursos insuficientes -OK-')

    def test_sin_coneccion(self):
        self.add_resource_to_plater()
        self.add_ver_and_road(self.player)
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':2, \'index\':7},\
                             {\'level\':2, \'index\':8}]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'El camino no se puede construir')
        print('Ubicacion desconectada -OK-')

    def test_camino_ocupado_otro_jugador(self):
        self.add_resource_to_plater()
        u = User(username='f', password='f')
        u.save()
        p = Player(username=u)
        p.save()
        self.add_ver_and_road(p)
        self.g.players.add(p)
        self.g.save()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':0, \'index\':0},\
                             {\'level\':0, \'index\':1}]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'Ya hay un camino construido en esa posición')
        print('Ubicacion acupada por jugador -OK-')

    def test_camino_inexistente(self):
        self.add_resource_to_plater()
        self.add_ver_and_road(self.player)
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'build_road',
                'payload': '[{\'level\':3, \'index\':-1},\
                             {\'level\':2, \'index\':8}]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'Camino invalido')
        print('Camino invalido -OK-')


class CardBuildRoadTest(TestCase, FillDatabase):
    def setUp(self):
        self.credentials = {
            'user': 'usuario',
            'pass': 'usuario123'}
        self.add_user_player()
        res = self.client.post('/users/login/',
                               self.credentials,
                               folow=True).json()
        self.token = 'Token ' + res['token']
        self.add_game()
        self.g = Game.objects.get(id=0)
        self.g.players.add(self.player)
        self.g.in_turn = self.player
        self.player.save()
        self.add_ver_and_road(self.player)
        self.g.save()
        self.c = Client()

    def test_esenario_exitoso(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':0, \'index\':1},\
                             {\'level\':1, \'index\':3}],\
                             [{\'level\':0, \'index\':1},\
                             {\'level\':0, \'index\':2}]]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Caminos construidos')
        self.assertEqual(3, len(self.player.roads.all()))
        self.assertEqual(4, len(self.player.cards.all()))
        print('Test escenario exitoso.',
              'Posiciones validas, jugador en turno -OK-')

    def test_caminos_encadenados(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':0, \'index\':1},\
                             {\'level\':1, \'index\':3}],\
                             [{\'level\':1, \'index\':3},\
                             {\'level\':1, \'index\':4}]]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Caminos construidos')
        self.assertEqual(3, len(self.player.roads.all()))
        self.assertEqual(4, len(self.player.cards.all()))
        print('Test Colocar dos caminos tal que se deben colocar \
en un orden especifico para que la accion se realice con exito -OK-')

    def test_caminos_encadenados_invertido(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':1, \'index\':3},\
                             {\'level\':1, \'index\':4}],\
                             [{\'level\':0, \'index\':1},\
                             {\'level\':1, \'index\':3}]]'},
            content_type='application/json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.json()['OK'],
                         'Caminos construidos')
        self.assertEqual(3, len(self.player.roads.all()))
        self.assertEqual(4, len(self.player.cards.all()))
        print('Test Pruebo la colocacion de los caminos en todos\
 los ordenes posibles -OK-')

    def test_caminos_invalidos(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':1, \'index\':15},\
                             {\'level\':0, \'index\':5}],\
                             [{\'level\':1, \'index\':12},\
                             {\'level\':0, \'index\':4}]]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'Caminos invalidos')
        self.assertEqual(1, len(self.player.roads.all()))
        self.assertEqual(5, len(self.player.cards.all()))
        print('Test caminos desconectados a las construcciones del jugador -OK-')

    def test_sin_carta_ConstruirCamino(self):
        request = self.c.post(
            '/games/0/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':1, \'index\':15},\
                             {\'level\':0, \'index\':5}],\
                             [{\'level\':1, \'index\':12},\
                             {\'level\':0, \'index\':4}]]'},
            content_type='application/json')
        self.assertEqual(0, len(self.player.cards.all()))
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'No se tiene la carta.')
        self.assertEqual(1, len(self.player.roads.all()))
        print('Test jugador sin carta de Construir Camino -OK-')

    def test_juego_inexistente(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/10/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':0, \'index\':1},\
                             {\'level\':1, \'index\':3}],\
                             [{\'level\':0, \'index\':1},\
                             {\'level\':0, \'index\':2}]]'},
            content_type='application/json')
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'No se encontro un juego con id = 10')
        print('Test juego inxesistente -OK-')

    def test_jugador_no_en_juego(self):
        self.add_card_to_player()
        request = self.c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token,
            data={
                'type': 'play_road_building_card',
                'payload': '[[{\'level\':0, \'index\':1},\
                             {\'level\':1, \'index\':3}],\
                             [{\'level\':0, \'index\':1},\
                             {\'level\':0, \'index\':2}]]'},
            content_type='application/json')
        g = Game.objects.get(id=1)
        g.players.add(self.player)
        g.save()
        self.assertEqual(400, request.status_code)
        self.assertEqual(request.json()['Error'],
                         'No es tu turno')
        print('Test jugador no en turno -OK-')


class TestMoveRobber(TestCase):
    def add_resource(self):
        for res in RESOURCE:
            r = Resource(type=res)
            r.save()

    def add_hex_pos(self):
        HexPosition(level=0, index=0).save()
        for lv in range(1, 3):
            for ind in range(0, 6 * lv):
                if(lv == 2 and ind == 5):
                    continue
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
            des = Resource(type="desert")
            des.save()
            pos = HexPosition(level=2, index=5)
            pos.save()
            hex = Hex(terrain=des,
                      position=pos,
                      token=5)
            hex.save()
            b.hexes.add(hex)
            b.save()
            for i in range(0, 18):
                hex = Hex(terrain=random.choice(lr),
                          position=lh[i],
                          token=tokens[i] % 11 + 2)
                hex.save()
                b.hexes.add(hex)
            b.save()

    def setUp(self):
        c = Client()
        user1 = User(username='jugador1', password='passdeJugador1')
        user1.save()
        user2 = User(username='jugador2', password='passdeJugador2')
        user2.save()
        user3 = User(username='jugador3', password='passdeJugador3')
        user3.save()
        user4 = User(username='jugador4', password='passdeJugador4')
        user4.save()
        data1 = {'user': 'jugador1', 'pass': 'passdeJugador1'}
        data2 = {'user': 'jugador2', 'pass': 'passdeJugador2'}
        data3 = {'user': 'jugador3', 'pass': 'passdeJugador3'}
        data4 = {'user': 'jugador4', 'pass': 'passdeJugador4'}
        request = c.post(
            '/users/login/',
            data1,
            content_type='application/json').json()
        self.token1 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data2,
            content_type='application/json').json()
        self.token2 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data3,
            content_type='application/json').json()
        self.token3 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data4,
            content_type='application/json').json()
        self.token4 = 'Token ' + request['token']
        self.player1 = Player(id=1, username=user1, colour='Blue')
        self.player1.save()
        self.player2 = Player(id=2, username=user2, colour='Red')
        self.player2.save()
        self.player3 = Player(id=3, username=user3, colour='Green')
        self.player3.save()
        self.player4 = Player(id=4, username=user4, colour='Orange')
        self.player4.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=1,
                         in_turn=self.player1,
                         name='Alto Juego',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.players.add(self.player1)
        self.game.players.add(self.player2)
        self.game.players.add(self.player3)
        self.game.save()

    def test_same_position(self):
        print('Testeando Cambio de robber a la misma posicion')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=5, y=2)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':0, 'index':0} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(request['Error'], 'Movimiento Inválido')
        print('-OK!-')

    def test_no_seven(self):
        print('Testeando Cambio de robber pero no habia salido 7')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=2)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':0, 'index':0} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(request['Error'], 'No salio 7, movimiento inválido')
        print('-OK!-')

    def test_robber_to_desert(self):
        print('Testeando Cambio de robber al desierto')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':2, 'index':5} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(
            request['Error'],
            'No se puede poner al robber en el desierto')
        print('-OK!-')

    def test_ok(self):
        print('Testeando movimiento valido de robber')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':2, 'index':8} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 200)
        print('-OK!-')

    def test_steal_resource(self):
        print('Testeando movimiento valido de robber con robado de recursos')
        c = Client()
        game = Game.objects.get(id=1)
        v = VertexPosition(level=1, index=12)
        v.save()
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        self.player2.cities.add(v)
        self.player2.save()
        r = Resource(type="ore")
        r.save()
        self.player2.resources.add(r)
        self.player2.save()
        cant_res = len(list(self.player2.resources.all()))
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':2, 'index':8},\
                                            'player': 'jugador2' }"},
            content_type='application/json')
        cant_new_res = len(list(self.player2.resources.all()))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(cant_res - cant_new_res, 1)
        print('-OK!-')

    def test_no_steal_resource(self):
        print('Testeando movimiento valido de robber con robado de recursos')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        cant_res = len(list(self.player2.resources.all()))
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'move_robber',
                'payload': "{ 'position': {'level':2, 'index':8}, 'player': 'jugador2' }"},
            content_type='application/json')
        cant_new_res = len(list(self.player2.resources.all()))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(cant_res - cant_new_res, 0)
        print('-OK!-')


class TestPlayKnightCard(TestCase):
    def add_resource(self):
        for res in RESOURCE:
            r = Resource(type=res)
            r.save()

    def add_hex_pos(self):
        HexPosition(level=0, index=0).save()
        for lv in range(1, 3):
            for ind in range(0, 6 * lv):
                if(lv == 2 and ind == 5):
                    continue
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
            des = Resource(type="desert")
            des.save()
            pos = HexPosition(level=2, index=5)
            pos.save()
            hex = Hex(terrain=des,
                      position=pos,
                      token=5)
            hex.save()
            b.hexes.add(hex)
            b.save()
            for i in range(0, 18):
                hex = Hex(terrain=random.choice(lr),
                          position=lh[i],
                          token=tokens[i] % 11 + 2)
                hex.save()
                b.hexes.add(hex)
            b.save()

    def setUp(self):
        c = Client()
        user1 = User(username='1', password='1')
        user1.save()
        user2 = User(username='2', password='2')
        user2.save()
        user3 = User(username='3', password='3')
        user3.save()
        user4 = User(username='4', password='4')
        user4.save()
        data1 = {'user': '1', 'pass': '1'}
        data2 = {'user': '2', 'pass': '2'}
        data3 = {'user': '3', 'pass': '3'}
        data4 = {'user': '4', 'pass': '4'}
        request = c.post(
            '/users/login/',
            data1,
            content_type='application/json').json()
        self.token1 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data2,
            content_type='application/json').json()
        self.token2 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data3,
            content_type='application/json').json()
        self.token3 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data4,
            content_type='application/json').json()
        self.token4 = 'Token ' + request['token']
        self.player1 = Player(id=1, username=user1, colour='Blue')
        self.player1.save()
        c = Card(type='knight')
        c.save()
        self.player1.cards.add(c)
        self.player1.save()
        self.player2 = Player(id=2, username=user2, colour='Red')
        self.player2.save()
        self.player3 = Player(id=3, username=user3, colour='Green')
        self.player3.save()
        self.player4 = Player(id=4, username=user4, colour='Orange')
        self.player4.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=1,
                         in_turn=self.player1,
                         name='Juego de prueba',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.players.add(self.player1)
        self.game.players.add(self.player2)
        self.game.players.add(self.player3)
        self.game.save()

    def test_same_position(self):
        print(
            'Testeando jugar caballero',
            'y hacer un cambio de robber a la misma posicion,',
            'chequeando que no se pueda')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=5, y=2)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':0, 'index':0} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(request['Error'], 'Movimiento Inválido')
        print('OK')

    def test_robber_to_desert(self):
        print(
            'Testeando jugar caballero',
            'y hacer un cambio de robber al desierto,',
            'chequeando que no se pueda')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':5} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        request = request.json()
        self.assertEqual(
            request['Error'],
            'No se puede poner al robber en el desierto')
        print('OK')

    def test_ok(self):
        print(
            'Testeando jugar carta de caballero válida,',
            'verificando movimiento del robber',
            'y desaparición de la carta de caballero dentro de las cartas del player')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':8} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 200)
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':8} }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        print('Testeando que no te queden cartas de caballer',
              'despues de jugar la unica que tenía')
        p1 = game.players.get(id=1)
        exists = p1.cards.filter(type='knight').exists()
        self.assertEqual(exists, False)
        print('OK')

    def test_steal_resource(self):
        print('Testeando jugar caballero',
              'con movimiento valido de robber con robado de recursos')
        c = Client()
        game = Game.objects.get(id=1)
        v = VertexPosition(level=1, index=12)
        v.save()
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        self.player2.cities.add(v)
        self.player2.save()
        r = Resource(type="ore")
        r.save()
        self.player2.resources.add(r)
        self.player2.save()
        cant_res = len(list(self.player2.resources.all()))
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':8},\
                                            'player': '2' }"},
            content_type='application/json')
        cant_new_res = len(list(self.player2.resources.all()))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(cant_res - cant_new_res, 1)
        print('OK')

    def test_no_steal_resource(self):
        print('Testeando jugar carta de caballero',
              'con movimiento valido de robber con robado de recursos',
              'pero el jugador a robar no tiene recursos')
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        game.dices = d
        game.save()
        cant_res = len(list(self.player2.resources.all()))
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':8},\
                                            'player': '2' }"},
            content_type='application/json')
        cant_new_res = len(list(self.player2.resources.all()))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(cant_res - cant_new_res, 0)
        print('OK')

    def test_no_knight_card(self):
        print('Testeando jugar carta de caballero',
              'sin de hecho tener la carta como jugador')
        p1 = self.game.players.get(id=1)
        card = p1.cards.get(type='knight')
        card.delete()
        p1.save()
        c = Client()
        game = Game.objects.get(id=1)
        d = Dice(x=2, y=5)
        d.save()
        self.game.dices = d
        self.game.save()
        request = c.post(
            '/games/1/player/actions',
            HTTP_AUTHORIZATION=self.token1,
            data={
                'type': 'play_knight_card',
                'payload': "{ 'position': {'level':2, 'index':8},\
                                            'player': '2' }"},
            content_type='application/json')
        self.assertEqual(request.status_code, 400)
        print('OK')


class TestDistributeResources(TestCase):
    def add_resource(self):
        for res in RESOURCE:
            r = Resource(type=res)
            r.save()

    def add_hex_pos(self):
        HexPosition(level=0, index=0).save()
        for lv in range(1, 3):
            for ind in range(0, 6 * lv):
                if(lv == 2 and ind == 5):
                    continue
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
            des = Resource(type="desert")
            des.save()
            pos = HexPosition(level=2, index=5)
            pos.save()
            hex = Hex(terrain=des,
                      position=pos,
                      token=5)
            hex.save()
            b.hexes.add(hex)
            b.save()
            for i in range(0, 18):
                hex = Hex(terrain=random.choice(lr),
                          position=lh[i],
                          token=tokens[i] % 11 + 2)
                hex.save()
                b.hexes.add(hex)
            b.save()

    def setUp(self):
        c = Client()
        user1 = User(username='jugador1', password='passdeJugador1')
        user1.save()
        user2 = User(username='jugador2', password='passdeJugador2')
        user2.save()
        user3 = User(username='jugador3', password='passdeJugador3')
        user3.save()
        user4 = User(username='jugador4', password='passdeJugador4')
        user4.save()
        data1 = {'user': 'jugador1', 'pass': 'passdeJugador1'}
        data2 = {'user': 'jugador2', 'pass': 'passdeJugador2'}
        data3 = {'user': 'jugador3', 'pass': 'passdeJugador3'}
        data4 = {'user': 'jugador4', 'pass': 'passdeJugador4'}
        request = c.post(
            '/users/login/',
            data1,
            content_type='application/json').json()
        self.token1 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data2,
            content_type='application/json').json()
        self.token2 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data3,
            content_type='application/json').json()
        self.token3 = 'Token ' + request['token']
        request = c.post(
            '/users/login/',
            data4,
            content_type='application/json').json()
        self.token4 = 'Token ' + request['token']
        self.player1 = Player(id=1, username=user1, colour='Blue')
        self.player1.save()
        self.player2 = Player(id=2, username=user2, colour='Red')
        self.player2.save()
        self.player3 = Player(id=3, username=user3, colour='Green')
        self.player3.save()
        self.player4 = Player(id=4, username=user4, colour='Orange')
        self.player4.save()
        dice = Dice(x=0, y=0)
        dice.save()
        robb = VertexPosition(level=0, index=0)
        robb.save()
        self.add_board()
        self.game = Game(id=1,
                         in_turn=self.player1,
                         name='Alto Juego',
                         dices=dice,
                         robber=robb,
                         board=Board.objects.get(id=1))
        self.game.players.add(self.player1)
        self.game.players.add(self.player2)
        self.game.players.add(self.player3)
        self.game.save()

    def test_repartirRecursos(self):
        i = 2
        hexes = self.game.board.hexes.filter(token=i)
        while (len(list(hexes)) == 0):
            i += 1
            hexes = self.game.board.hexes.filter(token=i)
        hexToTest = HexSerializer(list(hexes)[0]).data
        tokenNro = hexToTest['token']
        res = hexToTest['terrain']
        newDice = Dice(x=tokenNro, y=0)
        newDice.save()
        self.game.dices = newDice
        self.game.save()
        positionDesired = GetVertexs(list(hexes)[0])[0]
        settle = VertexPosition(
            level=positionDesired[0],
            index=positionDesired[1])
        settle.save()
        self.game.players.first().settlements.add(settle)
        self.game.save()
        before = self.game.players.first().resources_cards
        DistributeResources(1)
        self.assertGreaterEqual(before + 1,
                                self.game.players.first().resources_cards)
        print('Distribuir Recursos -OK-')

        print('Probando que no se asignen recusos en donde está el ladrón')
        newRobber = VertexPosition(
            level=hexToTest['position']['level'],
            index=hexToTest['position']['index'])
        newRobber.save()
        self.game.robber = newRobber
        self.game.save()
        before = self.game.players.first().resources_cards
        DistributeResources(1)
        self.assertEqual(before, self.game.players.first().resources_cards)
        print('-OK-')
