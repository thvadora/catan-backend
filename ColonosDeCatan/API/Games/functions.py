import random
import os
import json
from django.http import HttpResponse
from API.Games.models import Game, Dice
from API.Board.models import RoadPosition, VertexPosition, Resource
from API.Board.serializers import BoardStatusSerializer, HexSerializer
from API.Board.serializers import VertexPositionSerializer
from API.Games.serializers import DiceSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


def getNeighbors(vertex):
    neighbors = []
    f = open(os.path.join(os.path.dirname(__file__), 'neighbors.txt'), 'r')
    for line in f:
        data = line.split(' ')
        data.pop()
        data = list(int(x) for x in data)
        if (data[0], data[1]) == vertex:
            neighbors = data[2:]
            break
    neighbors = list(zip(*[iter(neighbors)] * 2))
    if vertex == (2, 13):
        neighbors.append((2, 12))
    return neighbors


def BuyCard(pk, user):
    game = Game.objects.get(id=pk)
    player = game.players.get(username=user)
    try:
        trigo = list(player.resources.filter(type="grain"))[0]
        oveja = list(player.resources.filter(type="wool"))[0]
        piedra = list(player.resources.filter(type="ore"))[0]
    except BaseException:
        return Response(
            {'Error':
                'No tienes los recursos suficientes'},
            status=status.HTTP_400_BAD_REQUEST)
    size = game.deck.all().count()
    if size == 0:
        return Response(
            {'Error':
                'No hay mas cartas disponibles para comprar'},
            status=status.HTTP_400_BAD_REQUEST)
    r_index = random.randint(0, size - 1)
    assigned_card = game.deck.all()[r_index]
    game.deck.remove(assigned_card)
    game.save()
    player.cards.add(assigned_card)
    player.development_cards = len(player.cards.all())
    player.save()
    player.resources.remove(trigo)
    player.resources.remove(oveja)
    player.resources.remove(piedra)
    player.resources_cards = len(player.resources.all())
    player.save()
    return Response({'OK': 'Carta comprada.'},
                    status=status.HTTP_200_OK)


def RollDices(pk):
    game = Game.objects.get(id=pk)
    new = Dice(x=random.randint(1, 6), y=random.randint(1, 6))
    new.save()
    game.dices = new
    game.save()


def Discard(pk):
    game = Game.objects.get(id=pk)
    if(game.dices.x + game.dices.y == 7):
        for player in game.players.all():
            n = player.resources.all().count()
            if(n > 7):
                eliminate = n / 2
                binary_list = []
                for i in range(0, n):
                    if(i < eliminate):
                        binary_list.append(1)
                    else:
                        binary_list.append(0)
                random.shuffle(binary_list)
                random.shuffle(binary_list)
                position = 0
                for resource in player.resources.all():
                    if(binary_list[position] == 1):
                        player.resources.remove(resource)
                        resource.delete()
                        player.resources_cards -= 1
                        player.save()
                    position += 1
                player.save()
    game.save()


def checkWinner(pk, user):
    game = Game.objects.get(id=pk)
    player = game.players.get(username=user)
    winner = False
    if (player.points + len(player.cards.filter(type='victory_point')) >= 10):
        game.winner = player
        game.save()
        winner = True
    return winner


def buildSettlement(pk, user, vlevel, vindex):
    game = Game.objects.get(id=pk)
    player = game.players.get(username=user)
    madera = player.resources.filter(type="lumber").first()
    lana = player.resources.filter(type="wool").first()
    ladrillo = player.resources.filter(type="brick").first()
    trigo = player.resources.filter(type="grain").first()
    round_number = int(game.turn_number / 4)
    if None in [madera, lana, ladrillo, trigo] and round_number > 1:
        return Response(
            {'Error':
                'No tienes los recursos suficientes'},
            status=status.HTTP_400_BAD_REQUEST)

    # CHEQUEAR QUE SI ESTOY EN LAS PRIMERAS RONDAS, SOLO PUEDA CONSTRUIR HASTA
    # DOS CASAS
    if round_number < 2 and player.settlements.all().count() >= 2:
        return Response(
            {'Error':
                'Solo puedes construir hasta 2 casas\
                    en las primeras dos rondas'},
            status=status.HTTP_400_BAD_REQUEST)

    # CHEQUEAR QUE NO HAYA PUEBLO EN ESE LUGAR
    for p in game.players.all():
        for r in p.settlements.all():
            t = (vlevel, vindex)
            if t == (r.level, r.index):
                return Response(
                    {'Error':
                     'Ya hay un pueblo construido en esa posición'},
                    status=status.HTTP_400_BAD_REQUEST)

    # CHEQUEAR QUE NO HAYA PUEBLOS A DISTANCIA MENOR QUE 2
    neighbors = getNeighbors((vlevel, vindex))
    for players in game.players.all():
        for settlements in players.settlements.all():
            s = (settlements.level, settlements.index)
            if s in neighbors or s == (vlevel, vindex):
                return Response(
                    {'Error':
                     'No se puede construir pueblo en el vertice deseado.'},
                    status=status.HTTP_400_BAD_REQUEST)

    # CHEQUEAR QUE EN EL VERTEX A CONSTRUIR HAYA UNA PUNTA DE UNA RUTA MIA
    if round_number > 1:
        ls = player.roads.all()
        ls = list((x.x, x.y) for x in ls)
        ls = list(x for t in ls for x in t)
        ls = list((x.level, x.index) for x in ls)
        if not (vlevel, vindex) in ls:
            return Response(
                {'Error':
                    'No se puede construir pueblo en el vertice deseado.'},
                status=status.HTTP_400_BAD_REQUEST)
    vx = VertexPosition(index=vindex, level=vlevel)
    vx.save()
    player.settlements.add(vx)
    player.points += 1
    if round_number > 1:
        player.resources.remove(madera)
        player.resources.remove(trigo)
        player.resources.remove(ladrillo)
        player.resources.remove(lana)
        player.resources_cards = len(player.resources.all())
    player.save()
    return Response(
        {'OK':
         'Pueblo creado.'},
        status=status.HTTP_200_OK)


def BankTrade(pk, user, give, recieve):
    game = Game.objects.get(id=pk)
    player = game.players.get(username=user)
    resourcesOfgiven = player.resources.filter(type=give)
    if len(resourcesOfgiven) < 4:
        return Response(
            {'Error':
                'No tienes los recursos suficientes'},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        elim = list(resourcesOfgiven)
        for x in range(0, 4):
            elim[x].delete()
        recieveRes = Resource(type=recieve)
        recieveRes.save()
        player.resources.add(recieveRes)
        player.save()
        player.resources_cards = len(player.resources.all())
        player.save()
        return Response(
            {'OK':
             'Intercambio con el Banco realizado.'},
            status=status.HTTP_200_OK)


def try_build_road(game, vertexes):
    player = game.in_turn
    v0 = (vertexes[0]['level'], vertexes[0]['index'])
    v1 = (vertexes[1]['level'], vertexes[1]['index'])
    vesinos = getNeighbors(v0)

    if v1 not in vesinos:
        return {'Error': 'Camino invalido'}
    # CHEQUEAR QUE NO HAYA RUTA EN ESTE LUGAR

    for p in game.players.all():
        for r in p.roads.all():
            rd = ((r.x.level, r.x.index), (r.y.level, r.y.index))
            if rd == (v0, v1) or rd == (v1, v0):
                return {'Error': 'Ya hay un camino construido en esa posición'}

    any_settlement_or_city_or_road = False

    for s in player.settlements.all():
        v = (s.level, s.index)
        if v == v0 or v == v1:
            any_settlement_or_city_or_road = True

    for s in player.cities.all():
        v = (s.level, s.index)
        if v == v0 or v == v1:
            any_settlement_or_city_or_road = True

    for r in player.roads.all():
        rd = [(r.x.level, r.x.index), (r.y.level, r.y.index)]
        if v0 in rd or v1 in rd:
            any_settlement_or_city_or_road = True

    if not any_settlement_or_city_or_road:
        return {'Error': 'El camino no se puede construir'}

    vx0 = VertexPosition(level=v0[0], index=v0[1])
    vx1 = VertexPosition(level=v1[0], index=v1[1])
    vx0.save()
    vx1.save()
    rd = RoadPosition(x=vx0, y=vx1)
    rd.save()
    player.roads.add(rd)
    player.save()
    return {'OK': rd}  # Si puedo construir el camino devuelvo el obj.


def buildRoad(game, player, vertexes):

    madera = player.resources.filter(type="lumber").first()
    ladrillo = player.resources.filter(type="brick").first()
    round_number = int(game.turn_number / 4)

    if None in [madera, ladrillo] and round_number > 1:
        return Response(
            {'Error':
                'No tienes los recursos suficientes'},
            status=status.HTTP_400_BAD_REQUEST)

    # CHEQUEAR QUE SI ESTOY EN LAS PRIMERAS RONDAS, SOLO PUEDA CONSTRUIR HASTA
    # DOS CASAS
    if round_number < 2 and player.roads.all().count() >= 2:
        return Response(
            {'Error':
                'Solo puedes construir hasta 2 caminos\
                    en las primeras dos rondas'},
            status=status.HTTP_400_BAD_REQUEST)

    val = try_build_road(game, vertexes)

    if 'OK' in val:
        if round_number > 1:
            player.resources.remove(madera)
            player.resources.remove(ladrillo)
            player.resources_cards = len(player.resources.all())
        player.save()
        return Response({'OK': 'Camino construido'},
                        status=status.HTTP_200_OK)
    else:
        return Response({'Error': val['Error']},
                        status=status.HTTP_400_BAD_REQUEST)


def PlayBuildRoadCard(game, roads):
    player = game.in_turn
    card = player.cards.filter(type="road_building").first()

    if card is None:
        return Response({'Error': 'No se tiene la carta.'},
                        status=status.HTTP_400_BAD_REQUEST)
    val = []
    roads.append(roads[0])

    for rd in roads:
        val.append(try_build_road(game, rd))

    if 'OK' in val[0] and 'OK' in val[1]:
        player.cards.remove(card)
        player.development_cards = len(player.cards.all())
        player.save()
        return Response({'OK': 'Caminos construidos'},
                        status=status.HTTP_200_OK)

    if 'OK' in val[1] and 'OK' in val[2]:
        player.cards.remove(card)
        player.development_cards = len(player.cards.all())
        player.save()
        return Response({'OK': 'Caminos construidos'},
                        status=status.HTTP_200_OK)

    for v in val:
        if 'OK' in v:
            player.roads.remove(v['OK'])
            player.development_cards = len(player.cards.all())
            player.save()
    return Response({'Error': 'Caminos invalidos'},
                    status=status.HTTP_400_BAD_REQUEST)


def validHexs():
    return [(0, 0),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
            (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11)]


def MoveRobber(pk, hexagon, steal, fromKnight, player):
    game = Game.objects.get(pk=pk)
    given_level = hexagon['position']['level']
    given_index = hexagon['position']['index']
    hex_pair = (given_level, given_index)
    for hex in game.board.hexes.all():
        if(given_index == hex.position.index and
           given_level == hex.position.level and
           hex.terrain.type == "desert"):
            return Response(
                {'Error':
                 'No se puede poner al robber en el desierto'},
                status=status.HTTP_400_BAD_REQUEST)
    if((game.robber.level == given_level and
        game.robber.index == given_index) or
       (hex_pair not in validHexs())):
        return Response(
            {'Error':
             'Movimiento Inválido'},
            status=status.HTTP_400_BAD_REQUEST)
    n_robber = VertexPosition(level=given_level, index=given_index)
    n_robber.save()
    game.robber = n_robber
    game.robber_moved = True
    game.save()
    if steal:
        try:
            playerToSteal = hexagon['player']
        except BaseException:
            return Response(
                {'Error':
                 'No introdujo player para robar recurso'},
                status=status.HTTP_400_BAD_REQUEST)
        return StealResource(pk, hexagon['player'], fromKnight, player)
    if fromKnight:
        knight_card = player.cards.filter(type='knight').first()
        player.cards.remove(knight_card)
        player.development_cards = len(player.cards.all())
        player.save()
        return Response(
            {'OK':
             'Carta de caballero jugada'},
            status=status.HTTP_200_OK)
    else:
        return Response(
            {'OK':
             'Robber cambiado de posición'},
            status=status.HTTP_200_OK)


def getVertexofHex(hex):
    dict_vertexs = {
        (0, 0): [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)], (1, 0): [
            (0, 0), (0, 1), (1, 3), (1, 2), (1, 1), (1, 0)], (1, 1): [
            (0, 1), (0, 2), (1, 6), (1, 5), (1, 4), (1, 3)], (1, 2): [
            (0, 3), (1, 9), (1, 8), (1, 7), (1, 6), (0, 2)], (1, 3): [
            (1, 12), (1, 11), (1, 10), (1, 9), (0, 3), (0, 4)], (1, 4): [
            (1, 14), (1, 13), (1, 12), (0, 4), (0, 5), (1, 15)], (1, 5): [
            (1, 16), (1, 15), (0, 5), (0, 0), (1, 0), (1, 17)], (2, 0): [
            (2, 29), (1, 17), (1, 0), (1, 1), (2, 1), (2, 0)], (2, 1): [
            (2, 1), (1, 1), (1, 2), (2, 4), (2, 3), (2, 2)], (2, 2): [
            (1, 2), (1, 3), (1, 4), (2, 6), (2, 5), (2, 4)], (2, 3): [
            (1, 4), (1, 5), (2, 9), (2, 8), (2, 7), (2, 6)], (2, 4): [
            (1, 6), (1, 7), (2, 11), (2, 10), (2, 9), (1, 5)], (2, 5): [
            (1, 8), (2, 14), (2, 13), (2, 12), (2, 11), (1, 7)], (2, 6): [
            (1, 10), (2, 16), (2, 15), (2, 14), (1, 8), (1, 9)], (2, 7): [
            (2, 9), (2, 18), (2, 17), (2, 16), (1, 10), (1, 11)], (2, 8): [
            (2, 21), (2, 20), (2, 19), (1, 11), (1, 12), (1, 13)], (2, 9): [
            (2, 23), (2, 22), (2, 21), (1, 13), (1, 14), (2, 24)], (2, 10): [
            (2, 25), (2, 24), (1, 14), (1, 15), (1, 16), (2, 26)], (2, 11): [
            (2, 27), (2, 26), (1, 16), (1, 17), (2, 29), (2, 28)]}
    x = hex.level
    y = hex.index
    return dict_vertexs[(x, y)]


def StealResource(pk, playerToSteal, fromKnight, player):
    game = Game.objects.get(id=pk)
    robber = game.robber
    user = User.objects.get(username=str(playerToSteal))
    p = game.players.get(username=user)
    vertexs = getVertexofHex(robber)
    for x, y in vertexs:
        for c in p.cities.all():
            if (c.level == x and c.index == y):
                res = list(p.resources.all())
                if(len(res) > 0):
                    index = random.randint(0, len(res) - 1)
                    player.resources.add(res[index])
                    player.save()
                    p.resources.remove(res[index])
                    player.resources_cards = len(player.resources.all())
                    p.save()
                    game.save()
                if fromKnight:
                    knight_card = player.cards.filter(type='knight').first()
                    player.cards.remove(knight_card)
                    player.development_cards = len(player.cards.all())
                    player.save()
                    return Response(
                        {
                            'OK': 'Carta de caballero jugada,\
                                robber cambiado de posición\
                                    y robado de recurso exitoso.'},
                        status=status.HTTP_200_OK)
                else:
                    return Response({'OK':
                                     'Robber cambiado de posición\
                                         y robado de recurso exitoso'},
                                    status=status.HTTP_200_OK)
        for s in p.settlements.all():
            if (s.level == x and s.index == y):
                res = list(p.resources.all())
                if(len(res) > 0):
                    index = random.randint(0, len(res) - 1)
                    player.resources.add(res[index])
                    player.resources_cards = len(player.resources.all())
                    player.save()
                    p.resources.remove(res[index])
                    p.resources_cards = len(p.resources.all())
                    p.save()
                    game.save()
                    if fromKnight:
                        knight_card = player.cards.filter(
                            type='knight').first()
                        player.cards.remove(knight_card)
                        player.development_cards = len(player.cards.all())
                        player.save()
                        return Response(
                            {
                                'OK': 'Carta de caballero jugada,\
                                    robber cambiado de posición\
                                        y robado de recurso exitoso.'},
                            status=status.HTTP_200_OK)
                    else:
                        return Response({'OK':
                                         'Robber cambiado de posición\
                                             y robado de recurso exitoso'},
                                        status=status.HTTP_200_OK)
    game.save()
    if fromKnight:
        knight_card = player.cards.filter(type='knight').first()
        player.cards.remove(knight_card)
        player.development_cards = len(player.cards.all())
        player.save()
        return Response(
            {
                'OK': 'Carta de caballero jugada,\
                    robber cambiado de posición\
                        y robado de recurso exitoso'},
            status=status.HTTP_200_OK)
    return Response(
        {'OK':
         'Robber cambiado de posición y robado de recurso exitoso'},
        status=status.HTTP_200_OK)


def GetVertexs(hex):
    hexSerializer = HexSerializer(hex).data
    level = hexSerializer['position']['level']
    index = hexSerializer['position']['index']

    vertexs = []

    if level == 0:
        for i in range(0, 6):
            vertexs.append((0, i))
    elif level == 1:
        for i in range(0, 2):
            vertexs.append((0, (index + i) % 6))
        for i in range(0, 4):
            vertexs.append((1, (3 * index + i) % 18))
    else:
        if index % 2 == 0:
            for i in range(-1, 2):
                vertexs.append((1, (index + index // 2 + i) % 18))
            for i in range(-1, 2):
                vertexs.append((2, (2 * index + index // 2 + i) % 30))
        else:
            for i in range(0, 2):
                vertexs.append((1, (index + index // 2 + i) % 18))
            for i in range(-1, 3):
                vertexs.append((2, (2 * index + index // 2 + i) % 30))
    return vertexs


def DistributeResources(pk):
    game = Game.objects.get(id=pk)
    if game.turn_number in [0, 1, 2, 3, 4, 5, 6]:
        return
    gameDice = DiceSerializer(game.dices).data
    numberRolled = gameDice['dice'][0] + gameDice['dice'][1]
    hexes = game.board.hexes.filter(token=numberRolled)

    robber = VertexPositionSerializer(game.robber).data
    robberPos = (robber['level'], robber['index'])
    for player in game.players.all():
        player.last_gained.clear()
    for hex in hexes:
        hexSerializer = HexSerializer(hex).data
        level = hexSerializer['position']['level']
        index = hexSerializer['position']['index']
        if (robberPos) != (level, index):
            vertexs = GetVertexs(hex)
            for player in game.players.all():
                settles = VertexPositionSerializer(
                    player.settlements, many=True).data
                for settle in settles:
                    if ((settle['level'], settle['index']) in vertexs):
                        resType = HexSerializer(hex).data['terrain']
                        if resType != 'desert':
                            resource = Resource(type=resType)
                            resource.save()
                            player.resources.add(resource)
                            player.last_gained.add(resource)
                            player.resources_cards = len(
                                player.resources.all())
                            player.save()

                cities = VertexPositionSerializer(
                    player.cities, many=True).data

                for citie in cities:
                    if (citie['level'], citie['index']) in vertexs:
                        resType = HexSerializer(
                            list(hex)[0]).data['terrain'].value
                        if resType != 'desert':
                            resource1 = Resource(type=resType)
                            resource1.save()
                            resource2 = Resource(type=resType)
                            resource2.save()
                            player.resources.add(resource1)
                            player.resources.add(resource2)
                            player.last_gained.add(resource1)
                            player.last_gained.add(resource2)
                            player.resources_cards = len(
                                player.resources.all())
                            player.save()
    game.save()


def roadOcupado(game, rd):
    for pl in game.players.all():
        rds = pl.roads.all()
        rds = [((r.x.level, r.x.index), (r.y.level, r.y.index)) for r in rds]
        if rd in rds or (rd[1], rd[0]) in rds:
            return True

    return False


def actionBuildRoad(game_id, action):
    game = Game.objects.get(id=game_id)
    player = game.in_turn
    round_number = int(game.turn_number / 4)
    # si estoy en las primeras dos rondas
    if round_number < 2:
        # si ya construi dos roads
        if player.roads.all().count() >= 2:
            return {
                'type': action,
                'payload': []
            }

    av_road_aux = []

    for st in player.settlements.all():
        vx = (st.level, st.index)
        vecinos = getNeighbors(vx)
        for ves in vecinos:
            av_road_aux.append((vx, ves))

    for st in player.cities.all():
        vx = (st.level, st.index)
        vecinos = getNeighbors(vx)
        for ves in vecinos:
            av_road_aux.append((vx, ves))

    for rd in player.roads.all():
        rd = [rd.x, rd.y]
        for st in rd:
            vx = (st.level, st.index)
            vecinos = getNeighbors(vx)
            for ves in vecinos:
                av_road_aux.append((vx, ves))

    av_road = []

    for rd in av_road_aux:
        if rd not in av_road and (
                rd[1],
                rd[0]) not in av_road and not roadOcupado(
                game,
                rd):
            av_road.append(rd)

    av_road = [[{'level': x[0][0], 'index': x[0][1]},
                {'level': x[1][0], 'index':x[1][1]}] for x in av_road]

    res = {
        'type': action,
        "payload": av_road
    }

    return res


def actionMoveRobber(game_id, action):
    game = Game.objects.get(id=game_id)
    result = []
    for hex in game.board.hexes.all():
        if hex.terrain != 'desert' and (
                hex.position.level != game.robber.level or
                hex.position.index != game.robber.index):
            neighbors = getVertexofHex(hex.position)
            possible = []
            for player in game.players.all():
                if game.in_turn == player:
                    continue
                constructions = list(
                    player.settlements.all()) + list(player.cities.all())
                for i in range(0, len(constructions)):
                    constructions[i] = (
                        constructions[i].level, constructions[i].index)
                for s in constructions:
                    if s in neighbors:
                        possible.append(player.username.username)
            # quito posibles duplicados
            players = []
            for p in possible:
                if p not in players:
                    players.append(p)
            # armo objecto
            js = {
                'position': {
                    'level': hex.position.level,
                    'index': hex.position.index},
                'players': players}
            result.append(js)
    return {'type': action, 'payload': result}


def actionBuildSettlement_NormalRound(game_id, action):
    game = Game.objects.get(id=game_id)
    player = game.in_turn
    # los lugares posibles siempre son bordes de una ruta propia
    availables_repeats = [
        (road.x.level, road.x.index)for road in player.roads.all()] + [
            (road.y.level, road.y.index) for road in player.roads.all()]
    availables = []
    # eliminar repetidos
    for x in availables_repeats:
        if x not in availables:
            availables.append(x)
    # chequear que no hayan personas con una settlement en los lugares posibles
    for x in game.players.all():
        player_cities = [(k.level, k.index) for k in x.cities.all()]
        player_settlements = [
            (k.level, k.index) for k in x.settlements.all()]
        for s in player_settlements:
            if s in availables:
                availables.remove(s)
        for s in player_cities:
            if s in availables:
                availables.remove(s)
    # chequear que los lugares posibles no tengan vecinos
    for x in game.players.all():
        player_cities = [(k.level, k.index) for k in x.cities.all()]
        player_settlements = [(k.level, k.index) for k in x.settlements.all()]
        for s in player_settlements:
            for n in getNeighbors(s):
                if n in availables:
                    availables.remove(n)
        for s in player_cities:
            for n in getNeighbors(s):
                if n in availables:
                    availables.remove(n)
    payload = [{'level': x[0], 'index': x[1]} for x in availables]
    return{'type': action, 'payload': payload}


def actionBuildSettlement_Round1And2(game_id, action):
    game = Game.objects.get(id=game_id)
    player = game.in_turn
    availables = []
    # todos los vertices pueden ser ubicacion de una nueva casa
    for x in range(0, 6):
        availables.append((0, x))
    for x in range(0, 18):
        availables.append((1, x))
    for x in range(0, 30):
        availables.append((2, x))
    # chequear que no hayan personas con una settlement en los lugares posibles
    for x in game.players.all():
        player_cities = [(k.level, k.index) for k in x.cities.all()]
        player_settlements = [
            (k.level, k.index) for k in x.settlements.all()]
        for s in player_settlements:
            if s in availables:
                availables.remove(s)
        for s in player_cities:
            if s in availables:
                availables.remove(s)
    # chequear que no tenga vecinos
    for x in game.players.all():
        player_cities = [(k.level, k.index) for k in x.cities.all()]
        player_settlements = [(k.level, k.index) for k in x.settlements.all()]
        for s in player_settlements:
            for n in getNeighbors(s):
                if n in availables:
                    availables.remove(n)
        for s in player_cities:
            for n in getNeighbors(s):
                if n in availables:
                    availables.remove(n)

    payload = [{'level': x[0], 'index': x[1]} for x in availables]
    return{'type': action, 'payload': payload}


def actionBuildSettlement(game_id, action):
    game = Game.objects.get(id=game_id)
    round_number = int(game.turn_number / 4)
    # si estoy en las primeras dos rondas
    if round_number < 2:
        player = game.in_turn
        # si ya construi dos casas
        if player.settlements.all().count() >= 2:
            return {
                'type': action,
                "payload": []
            }
        return actionBuildSettlement_Round1And2(game_id=game_id, action=action)
    return actionBuildSettlement_NormalRound(game_id=game_id, action=action)


def actionBankTrade():
    return {'type': 'bank_trade'}


def actionEndTurn():
    return {'type': 'end_turn'}


def actionBuyCard():
    return {'type': 'buy_card'}


def handleAvailableActions(game_id, player_username):
    game = Game.objects.get(id=game_id)
    round_number = int(game.turn_number / 4)
    player = game.in_turn
    if(player_username != player.username.username or game.winner):
        return Response([],
                        status=status.HTTP_200_OK)

    settlements = player.settlements.all().count()
    roads = player.roads.all().count()
    resources = [r.type for r in player.resources.all()]
    cards = [c.type for c in player.cards.all()]
    actions = []
    if round_number == 0:
        if settlements == 0:
            actions.append(actionBuildSettlement(game_id, 'build_settlement'))
        elif roads == 0:
            actions.append(actionBuildRoad(game_id, 'build_road'))
        else:
            actions.append(actionEndTurn())
    elif round_number == 1:
        if settlements == 1:
            actions.append(actionBuildSettlement(game_id, 'build_settlement'))
        elif roads == 1:
            actions.append(actionBuildRoad(game_id, 'build_road'))
        else:
            actions.append(actionEndTurn())
    elif game.dices.x + game.dices.y == 7 and not game.robber_moved:
        actions.append(actionMoveRobber(game_id, 'move_robber'))
    else:
        end = {'type': 'end_turn', 'payload': []}
        actions.append(end)
        need = ['lumber', 'wool', 'brick', 'grain']
        flag = True
        for r in need:
            flag = flag and (r in resources)
        if flag:
            actions.append(actionBuildSettlement(game_id, 'build_settlement'))
        need = ['lumber', 'brick']
        flag = True
        for r in need:
            flag = flag and (r in resources)
        if flag:
            actions.append(actionBuildRoad(game_id, 'build_road'))
        need = ['wool', 'ore', 'grain']
        flag = True
        for r in need:
            flag = flag and (r in resources)
        if flag:
            actions.append(actionBuyCard())
        if 'knight' in cards:
            actions.append(actionMoveRobber(game_id, 'play_knight_card'))
        lumber = 0
        grain = 0
        brick = 0
        wool = 0
        ore = 0
        for x in resources:
            lumber += (x == "lumber")
            grain += (x == "grain")
            brick += (x == "brick")
            wool += (x == "wool")
            ore += (x == "ore")

        if lumber >= 4 or grain >= 4 or brick >= 4 or wool >= 4 or ore >= 4:
            actions.append(actionBankTrade())

    return Response(actions,
                    status=status.HTTP_200_OK)
