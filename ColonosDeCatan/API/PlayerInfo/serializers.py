from rest_framework import serializers
from API.PlayerInfo.models import Player
from API.Board.models import VertexPosition
from API.Board.serializers import ResourceSerializer
from API.Board.serializers import VertexPositionSerializer
from API.Board.serializers import RoadPositionSerializer
from API.Board.serializers import CardSerializer
from API.User.serializers import UserSerializer


class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    settlements = VertexPositionSerializer(many=True)
    cities = VertexPositionSerializer(many=True)
    roads = serializers.SerializerMethodField()
    last_gained = serializers.SerializerMethodField()
    victory_points = serializers.SerializerMethodField()

    def get_last_gained(self, obj):
        res = [x.type for x in obj.last_gained.all()]
        return res

    def get_username(self, obj):
        return obj.username.username

    def get_victory_points(self, obj):
        return obj.points

    def get_roads(self, obj):
        l = []
        for k in obj.roads.all():
            ll = [{'level': k.x.level, 'index': k.x.index},
                  {'level': k.y.level, 'index': k.y.index}]
            l.append(ll)
        return l

    class Meta:
        model = Player
        fields = [
            'username',
            'colour',
            'settlements',
            'cities',
            'roads',
            'development_cards',
            'resources_cards',
            'victory_points',
            'last_gained']


class PlayerInfoSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()

    def get_cards(self, obj):
        cards = [x.type for x in obj.cards.all()]
        return cards

    def get_resources(self, obj):
        res = [x.type for x in obj.resources.all()]
        return res

    class Meta:
        model = Player
        fields = ['resources', 'cards']
