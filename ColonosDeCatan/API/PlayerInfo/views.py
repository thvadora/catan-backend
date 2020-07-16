from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from API.PlayerInfo.serializers import PlayerInfoSerializer
from API.Games.models import Game
from API.PlayerInfo.models import Player


class PlayerPersonalInfo (APIView):
    def get(self, request, id):
        try:
            game = Game.objects.get(id=id)
        except Game.DoesNotExist:
            return Response(
                {'error': 'No existe el Juego con id: ' + str(id)},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            player = game.players.get(username=request.user)
            serializer = PlayerInfoSerializer(player)
            return Response(serializer.data)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Jugador no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
