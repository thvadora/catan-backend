from rest_framework import serializers
from API.Games.models import Action, Dice, Game
from API.User.serializers import UserSerializer
from API.Board.serializers import VertexPositionSerializer
from API.PlayerInfo.serializers import PlayerSerializer


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['type']


class DiceSerializer(serializers.ModelSerializer):
    dice = serializers.SerializerMethodField()

    def get_dice(self, obj):
        return [obj.x, obj.y]

    class Meta:
        model = Dice
        fields = ['dice']


class CurrentTurnSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    dice = DiceSerializer()

    class Meta:
        model = Game
        fields = ['user', 'dice']


class GameStatusSerializer(serializers.ModelSerializer):
    current_turn = serializers.SerializerMethodField()
    players = PlayerSerializer(many=True)
    robber = VertexPositionSerializer()
    winner = serializers.SerializerMethodField()

    def get_winner(self, obj):
        if obj.winner is not None:
            return obj.winner.username.username
        else: 
            return ""

    def get_current_turn(self, obj):
        user = obj.in_turn.username
        dice = obj.dices
        return {'user': user.username,
                'dice': [dice.x, dice.y]}

    class Meta:
        model = Game
        fields = ['id', 'name', 'current_turn', 'players',
                  'robber', 'winner']


class GameSerializer(serializers.ModelSerializer):
    in_turn = serializers.SerializerMethodField()

    def get_in_turn(self, obj):
        return obj.in_turn.username.username

    class Meta:
        model = Game
        fields = ['id', 'name', 'in_turn']


class StartGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['id']
