from rest_framework import serializers
from API.Room.models import Room
from API.Board.serializers import BoardSerializer
from API.Games.serializers import StartGameSerializer
from API.PlayerInfo.serializers import PlayerSerializer
from API.User.serializers import UserSerializer


class RoomSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.username

    def get_players(self, obj):
        players = [x.username.username for x in obj.players.all()]
        return players

    def get_game_id(self, obj):
        if obj.game_has_started:
            return obj.game.id
        else:
            return None

    class Meta:
        model = Room
        fields = ['id', 'name', 'owner', 'players',
                  'max_players', 'game_has_started', 'game_id']
