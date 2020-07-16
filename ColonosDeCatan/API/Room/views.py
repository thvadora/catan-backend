from django.http import Http404
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from API.Room.models import Room
from API.Board.models import Board
from API.Games.models import Game
from API.PlayerInfo.models import Player
from API.User.serializers import UserSerializer
from API.Room.serializers import RoomSerializer
from API.Room.functions import CreateGame, getRoomById


class RoomCreateOrGet(APIView):

    def get(self, request, format=None):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        name = request.data.get("name")
        board_id = request.data.get("board_id")
        user = request.user
        if not name:
            return Response(
                {'Error': 'No se encontró el campo \'name\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not board_id:
            return Response(
                {'Error': 'No se encontró el campo \'board_id\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {'Error': 'No existe el tablero con \'board_id\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        room = Room.objects.create(name=name, owner=user, board=board)
        room.save()
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomJoinGetorDelete(APIView):
    def get(self, request, pk, format=None):
        room = getRoomById(pk)
        if isinstance(room, tuple):
            return room[1]
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        COLOURS = ['Blue', 'Red', 'Green', 'Yellow']
        room = getRoomById(pk)
        if isinstance(room, tuple):
            return room[1]
        try:
            already_in = room.players.get(username=request.user)
        except BaseException:
            count = room.players.all().count()
            if (count < room.max_players) and not ():
                player = Player(username=request.user,
                                colour=COLOURS[count]
                                )
                player.save()
                room.players.add(player)
            else:
                return Response(
                    {'error': 'Lobby lleno'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'OK': 'Unido al room con éxito'},
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk, *args, **kwargs):
        room = getRoomById(pk)
        if isinstance(room, tuple):
            return room[1]
        if room.players.all().count() != 4:
            return Response(
                {'error':
                 'No hay suficientes jugadores para comenzar el juego'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user != room.owner:
            return Response(
                {'error': 'Solo el dueño puede comenzar la partida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return CreateGame(room=room)

    def delete(self, request, pk, *args, **kwargs):
        room = getRoomById(pk)
        if isinstance(room, tuple):
            return room[1]
        if room.owner != request.user:
            return Response(
                {'error': 'Sólo el dueño puede eliminar la partida'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if room.game_has_started:
            return Response(
                {'error': 'No se puede borrar una partida ya comenzada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        room.delete()
        return Response(
            {'OK': 'Room eliminada'},
            status=status.HTTP_200_OK
        )
