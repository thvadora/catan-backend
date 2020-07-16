from rest_framework import serializers
from API.Transaction.models import Response, Transaction
from API.User.serializers import UserSerializer
from API.Board.serializers import ResourceSerializer


class ResponseSerializer(serializers.ModelSerializer):
    player = UserSerializer()

    class Meta:
        model = Response
        fields = ['player', 'accepted']


class TransactionSerializer(serializers.ModelSerializer):
    offer = ResourceSerializer(many=True)
    requester = UserSerializer()
    responses = ResponseSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['offer', 'requested', 'requester', 'responses']
