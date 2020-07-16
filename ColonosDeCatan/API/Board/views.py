from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from API.Board.models import Board
from API.Board.serializers import BoardSerializer


class boardList(APIView):
    def get(self, request):
        board = Board.objects.all()
        serializer = BoardSerializer(board, many=True)
        return Response(serializer.data)
