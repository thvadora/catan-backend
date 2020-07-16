from rest_framework import serializers
from API.Board.models import Board, Resource, Card
from API.Board.models import VertexPosition
from API.Board.models import Hex, HexPosition
from API.Board.models import RoadPosition


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['type']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['type']


class HexPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HexPosition
        fields = ['level', 'index']


class HexSerializer(serializers.ModelSerializer):
    position = HexPositionSerializer()
    terrain = serializers.SerializerMethodField()

    def get_terrain(self, obj):
        return obj.terrain.type

    class Meta:
        model = Hex
        fields = ['position', 'terrain', 'token']


class VertexPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VertexPosition
        fields = ['level', 'index']


class RoadPositionSerializer(serializers.ModelSerializer):
    x = VertexPositionSerializer()
    y = VertexPositionSerializer()

    class Meta:
        model = Hex
        fields = ['x', 'y']


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name']


class BoardStatusSerializer(serializers.ModelSerializer):
    hexes = HexSerializer(many=True)

    class Meta:
        model = Board
        fields = ['hexes']
