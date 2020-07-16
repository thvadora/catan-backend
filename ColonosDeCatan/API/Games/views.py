from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from API.Board.serializers import *
from API.Games.models import Game
from API.Games.serializers import *
from API.Games.functions import *
import json


class boardStatus(APIView):
    def get(self, request, id):
        try:
            game = Game.objects.get(id=id)
        except Game.DoesNotExist:
            return Response(
                {'Error':
                 'No se encontro un juego con id = ' + str(id)},
                status=status.HTTP_400_BAD_REQUEST)
        board = game.board
        serializer = BoardStatusSerializer(board)
        return Response(serializer.data)


class GetGame(APIView):
    def get(self, request, pk):
        try:
            game = Game.objects.get(id=pk)
        except Game.DoesNotExist:
            return Response(
                {'Error':
                 'No se encontro un juego con id = ' + str(pk)},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = GameStatusSerializer(game)
        return Response(serializer.data)


class ListGames(APIView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)


class PlayAction(APIView):
    def get(self, request, pk):
        try:
            game = Game.objects.get(id=pk)
        except Game.DoesNotExist:
            return Response(
                {'Error':
                 'No se encontro un juego con id = ' + str(pk)},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            player = game.players.get(username=request.user)
        except BaseException:
            return Response(
                {'Error':
                 'No eres jugador de este juego'},
                status=status.HTTP_400_BAD_REQUEST)
        player_username = game.players.get(
            username=request.user).username.username
        return handleAvailableActions(pk, player_username)

    def post(self, request, pk, *args, **kwargs):
        action_type = request.data.get("type")
        payload = request.data.get("payload")
        if payload is not None and payload is not '':
            payload = str(payload).replace("'", "\"")
            payload = json.loads(payload)
        try:
            game = Game.objects.get(id=pk)
        except Game.DoesNotExist:
            return Response(
                {'Error':
                 'No se encontro un juego con id = ' + str(pk)},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            player = game.players.get(username=request.user)
        except BaseException:
            return Response(
                {'Error':
                 'No eres jugador de este juego'},
                status=status.HTTP_400_BAD_REQUEST)

        if game.in_turn != player:
            return Response(
                {'Error':
                    'No es tu turno'},
                status=status.HTTP_400_BAD_REQUEST)

        # TODAS LAS POSIBILIDADES DE ACCIONES
        if action_type == "buy_card":
            return BuyCard(pk=pk, user=request.user)
        elif action_type == "end_turn":
            if game.turn_number in (0, 1, 2, 3) and player.settlements.all(
            ).count() != 1 and player.roads.all().count() != 1:
                return Response(
                    {
                        'Error': 'Debes construir un poblado\
                            y una carretera para continuar'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif (game.turn_number in (4, 5, 6, 7) and
                  player.settlements.all().count() != 2 and
                  player.roads.all().count() != 2):
                return Response(
                    {
                        'Error': 'Debes construir un poblado\
                            y una carretera para continuar'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                winner = checkWinner(pk=pk, user=request.user)
                if winner:
                    return Response({'OK': 'Partida ganada'},
                                    status=status.HTTP_200_OK)
                RollDices(pk=pk)
                Discard(pk=pk)
                DistributeResources(pk=pk)
                # siempre al final
                game = Game.objects.get(id=pk)
                game.turn_number += 1
                game.save()
                player_list = list(game.players.all())
                list_size = len(player_list)
                game.in_turn = player_list[game.turn_number % list_size]
                game.robber_moved = False
                game.save()
                return Response({'OK': 'Turno terminado'},
                                status=status.HTTP_200_OK)
        elif action_type == "build_settlement":
            return buildSettlement(pk=pk,
                                   user=request.user,
                                   vlevel=payload['level'],
                                   vindex=payload['index'])
        elif action_type == "bank_trade":
            resgive = payload['give']
            resrecieve = payload['receive']
            if resgive == resrecieve:
                return Response(
                    {'Error':
                     'No puedes intercambiar el mismo recurso'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return BankTrade(pk=pk,
                                 user=request.user,
                                 give=resgive,
                                 recieve=resrecieve)
        elif action_type == "build_road":
            return buildRoad(game=game,
                             player=player,
                             vertexes=payload)
        elif action_type == "play_road_building_card":
            return PlayBuildRoadCard(game=game,
                                     roads=payload)
        elif action_type == "move_robber":
            hex = payload
            game = Game.objects.get(id=pk)
            if(game.dices.x + game.dices.y != 7):
                return Response(
                    {'Error':
                     'No salio 7, movimiento inválido'},
                    status=status.HTTP_400_BAD_REQUEST)
            steal = True
            try:
                # solo para saber si tengo que robar recurso,
                # es decir, si paso un player
                t = hex['player']
            except BaseException:
                steal = False
            return MoveRobber(
                pk=pk,
                hexagon=hex,
                steal=steal,
                fromKnight=False,
                player=player)
        elif action_type == "play_knight_card":
            hex = payload
            knight_card = player.cards.filter(type='knight').exists()

            if knight_card is False:
                return Response(
                    {'Error':
                     'No cuentas con una carta de caballero'},
                    status=status.HTTP_400_BAD_REQUEST)
            steal = True
            try:
                t = hex['player']
            except BaseException:
                steal = False
            return MoveRobber(
                pk=pk,
                hexagon=hex,
                steal=steal,
                fromKnight=True,
                player=player)
        else:
            return Response(
                {'Error':
                 'Accion no válida'},
                status=status.HTTP_400_BAD_REQUEST)
