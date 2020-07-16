from django.db import models
from API.Board.models import Board, VertexPosition
from API.Board.models import RoadPosition, Resource, Card
from API.PlayerInfo.models import Player


class Action(models.Model):
    type = models.CharField(max_length=50, primary_key=True)

    def save(self, *args, **kwargs):
        super(Action, self).save(*args, **kwargs)


class Dice(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()

    def save(self, *args, **kwargs):
        super(Dice, self).save(*args, **kwargs)


class Game(models.Model):
    name = models.CharField(max_length=100)
    turn_number = models.IntegerField(default=0)
    in_turn = models.OneToOneField(
        Player, related_name='in_turn', on_delete=models.CASCADE, null=True)
    dices = models.OneToOneField(
        Dice, related_name='dice', on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, related_name='players')
    robber_moved = models.BooleanField(default=False)
    robber = models.OneToOneField(VertexPosition, on_delete=models.CASCADE)
    deck = models.ManyToManyField(Card)
    longest_path = models.OneToOneField(
        Player,
        related_name='longest_path',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    largest_army = models.OneToOneField(
        Player,
        related_name='largest_army',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    winner = models.OneToOneField(
        Player,
        related_name='winner',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)
