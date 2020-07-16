from django.test import TestCase, Client
from API.Board.models import *
from API.User.models import User
from API.Board.serializers import *
from API.User.serializers import UserSerializer
from rest_framework.renderers import JSONRenderer
import random
import json

RESOURCE = ["brick", "lumber", "wool", "grain", "ore"]


class BoardTest(TestCase):
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

    def add_user(self):
        if not User.objects.filter(username=self.credentials['user']).exists():
            user = User(username=self.credentials['user'],
                        password=self.credentials['pass'])
            user.save()

    def setUp(self):
        self.credentials = {
            'user': 'usuario',
            'pass': 'usuario123'}
        self.add_user()
        res = self.client.post('/users/login/',
                               self.credentials,
                               folow=True).json()
        self.token = 'Token ' + res['token']

    def test_BoardList(self):
        self.add_board(100)
        res = self.client.get('/boards',
                              HTTP_AUTHORIZATION=self.token)
        boards = list(BoardSerializer(Board.objects.all(), many=True).data)
        boards = list(json.loads(JSONRenderer().render(x)) for x in boards)
        self.assertListEqual(res.json(), boards)
        Board.objects.all().delete()
        print('Listado de tableros -OK-')

    def test_vacio(self):
        res = self.client.get('/boards', HTTP_AUTHORIZATION=self.token)
        self.assertListEqual(res.json(), [])
        print('Lista vacia -OK-')

    def test_board_serializer(self):
        b = Board(name='test', id=1)
        b.save()
        res = self.client.get('/boards', HTTP_AUTHORIZATION=self.token)
        exp = {'name': 'test', 'id': 1}
        self.assertDictEqual(res.json()[0], exp)
        b.delete()
        print('Serializador correcto -OK-')

    def test_stress(self):
        print('Estresando servidor')
        self.add_board(500)
        for i in range(0, 1000):
            res = self.client.get('/boards',
                                  HTTP_AUTHORIZATION=self.token)
            boards = list(BoardSerializer(Board.objects.all(), many=True).data)
            boards = list(json.loads(JSONRenderer().render(x)) for x in boards)
            self.assertListEqual(res.json(), boards)
        Board.objects.all().delete()
        print('Test estresante superado -OK-')
