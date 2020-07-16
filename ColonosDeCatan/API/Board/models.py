from django.db import models


class Resource(models.Model):
    type = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)


class Card(models.Model):
    type = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        super(Card, self).save(*args, **kwargs)


class HexPosition(models.Model):
    level = models.IntegerField()
    index = models.IntegerField()

    def save(self, *args, **kwargs):
        super(HexPosition, self).save(*args, **kwargs)


class VertexPosition(models.Model):
    level = models.IntegerField()
    index = models.IntegerField()

    def save(self, *args, **kwargs):
        super(VertexPosition, self).save(*args, **kwargs)


class RoadPosition(models.Model):
    x = models.ForeignKey(VertexPosition, related_name='x',
                          on_delete=models.CASCADE)
    y = models.ForeignKey(VertexPosition, related_name='y',
                          on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(RoadPosition, self).save(*args, **kwargs)


class Hex(models.Model):
    position = models.ForeignKey(HexPosition, related_name='position',
                                 on_delete=models.CASCADE)
    terrain = models.ForeignKey(
        Resource, related_name='resource', on_delete=models.CASCADE)
    token = models.IntegerField()
    vertexes = models.ManyToManyField(
        VertexPosition, related_name='hex_vertexes')
    roads = models.ManyToManyField(RoadPosition, related_name='hex_roads')

    def save(self, *args, **kwargs):
        super(Hex, self).save(*args, **kwargs)


class Board(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    hexes = models.ManyToManyField(Hex)

    def save(self, *args, **kwargs):
        super(Board, self).save(*args, **kwargs)
