from API.Games.models import Game, Dice, Player
from API.Games.serializers import *
from API.Board.models import *
from API.Board.serializers import *
from API.Room.models import Room
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import random
import os


def CreateGame(room):
    if room.game_has_started:
        return Response({'error': 'El juego ya empezo.'},
                        status=status.HTTP_400_BAD_REQUEST)

    dado = Dice(x=random.randint(1, 6), y=random.randint(1, 6))
    dado.save()
    tablero = room.board

    # Obtener Hex con el Desierto
    for x in tablero.hexes.all():
        terreno = ResourceSerializer(x.terrain)
        if terreno.data['type'] == 'desert':
            ladron = VertexPosition(
                level=x.position.level,
                index=x.position.index)
            ladron.save()
            break
        else:
            continue

    # Crear el Juego
    game = Game(
        name='Juego de {}'.format(room.owner.username),
        id=room.id,
        dices=dado,
        robber=ladron,
        board=tablero
    )
    game.save()

    # Añadir los jugadores
    players = list(room.players.all())
    for x in players:
        game.players.add(x)

    game.save()

    game.in_turn = game.players.all().first()

    game.save()

    # Agregar el mazo
    for i in range(0, 25):
        if i < 14:
            c = Card(type="knight")
            c.save()
            game.deck.add(c)
            game.save()
        elif i < 16:
            c = Card(type="monopoly")
            c.save()
            game.deck.add(c)
            game.save()
        elif i < 18:
            c = Card(type="road_building")
            c.save()
            game.deck.add(c)
            game.save()
        elif i < 20:
            c = Card(type="year_of_plenty")
            c.save()
            game.deck.add(c)
            game.save()
        else:
            c = Card(type="victory_point")
            c.save()
            game.deck.add(c)
            game.save()

    # Terminar de modificar el lobby
    room.game_has_started = True
    room.game = game
    room.save()

    return Response({'OK': 'Juego creado.'},
                    status=status.HTTP_200_OK)


def getRoomById(id):
    try:
        room = Room.objects.get(id=id)
        return room
    except Room.DoesNotExist:
        return (-1, Response(
                {'error': 'No existe Lobby con id: ' + str(id)},
                status=status.HTTP_400_BAD_REQUEST
                ))
