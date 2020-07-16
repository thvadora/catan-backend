from django.db import models
from API.User.models import User
from API.Board.models import VertexPosition, RoadPosition
from API.Board.models import Resource, Card


class Player(models.Model):
    username = models.ForeignKey(
        User, on_delete=models.CASCADE)
    colour = models.CharField(max_length=30)
    settlements = models.ManyToManyField(
        VertexPosition,
        related_name='settlements')
    cities = models.ManyToManyField(
        VertexPosition, related_name='cities')
    roads = models.ManyToManyField(
        RoadPosition, related_name='roads')
    development_cards = models.IntegerField(default=0)
    resources_cards = models.IntegerField(default=0)
    resources = models.ManyToManyField(
        Resource, related_name='res')
    last_gained = models.ManyToManyField(
        Resource, related_name='last_gained')
    cards = models.ManyToManyField(
        Card, related_name='cards')
    points = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super(Player, self).save(*args, **kwargs)
