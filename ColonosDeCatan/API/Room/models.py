from django.db import models
from API.PlayerInfo.models import Player
from API.User.models import User
from API.Games.models import Game
from API.Board.models import Board


class Room(models.Model):
    name = models.CharField(max_length=100, default="")
    owner = models.ForeignKey(
        User, related_name='own', on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)
    max_players = models.IntegerField(default=4)
    board = models.ForeignKey(
        Board, related_name='board', on_delete=models.CASCADE, null=True)
    game_has_started = models.BooleanField(default=False)
    game = models.OneToOneField(
        Game, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Room, self).save(*args, **kwargs)
