from API.Board.models import *
from API.Games.models import *
from API.PlayerInfo.models import *
from API.User.models import *
from API.Room.models import *
from API.Transaction.models import *
from API.Board.serializers import *
from API.Games.serializers import *
from API.PlayerInfo.serializers import *
from API.User.serializers import *
from API.Room.serializers import *
from API.Transaction.serializers import *
from rest_framework.renderers import JSONRenderer
import json

l = [
    ("Hex", Hex, HexSerializer),
    ("VertexPosition", VertexPosition, VertexPositionSerializer),
    ("HexPos", HexPosition, HexPositionSerializer),
    ("Resource", Resource, ResourceSerializer),
    ("Board", Board, BoardSerializer),
    ("BoardStatus", Board, BoardStatusSerializer),
    ("Games", Game, GameSerializer),
    ("GameStatus", Game, GameStatusSerializer),
    ('Player', Player, PlayerSerializer),
    ('PlayerInfo', Player, PlayerInfoSerializer),
    ('Users', User, UserSerializer),
    ('Room', Room, RoomSerializer),
    ('Dice', Dice, DiceSerializer),
]


def printALL(name=None):
    if name is None:
        for N, M, F in l:
            print(N)
            print(json.dumps(json.loads(JSONRenderer().render(
                F(M.objects.all(), many=True).data)), indent=4))
            print(' ')
    else:
        for N, M, F in l:
            if N == name:
                print(N)
                print(json.dumps(json.loads(JSONRenderer().render(
                    F(M.objects.all(), many=True).data)), indent=4))
                print(' ')


def deleteALL():
    for N, M, F in l:
        M.objects.all().delete()
