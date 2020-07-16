from django.db import models
from API.PlayerInfo.models import Player
from API.Board.models import Resource


class Response(models.Model):
    player = models.OneToOneField(
        Player, on_delete=models.CASCADE, blank=True, null=True)
    accepted = models.BooleanField()

    def save(self, *args, **kwargs):
        super(Response, self).save(*args, **kwargs)


class Transaction(models.Model):
    offer = models.ManyToManyField(Resource, related_name='offer')
    request = models.ManyToManyField(Resource, related_name='request')
    requester = models.ForeignKey(
        Player, related_name='request', on_delete=models.CASCADE)
    responses = models.ManyToManyField(Response)
    status = models.CharField(max_length=15, null=True)
    winner = models.OneToOneField(
        Player, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)
