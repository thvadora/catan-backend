from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db.utils import IntegrityError
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from API.User.models import User


class RegisterUser(APIView):
    permission_classes = (AllowAny, )
    """
    Registrar a una persona en el sistema como usuario.
    """

    def post(self, request, *args, **kwargs):
        username = request.data.get("user")
        password = request.data.get("pass")
        if not username:
            return Response(
                {'error': 'No se encontró el campo \'user\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {'error': 'No se encontró el campo \'pass\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(username) > 150:
            return Response(
                {'error': 'El campo \'user\'' +
                 'no debe exceder los 150 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(username) <= 0:
            return Response(
                {'error': 'El campo \'user\' no debe tener 0 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if " " in username:
            return Response(
                {'error': 'El campo \'user\' no debe contener espacios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if " " in password:
            return Response(
                {'error': 'El campo \'pass\' no debe contener espacios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < 8:
            return Response(
                {'error': 'El campo \'pass\'' +
                 'no debe tener menos de 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if user is not None:
                return Response(
                    {'error': 'Ya existe el usuario'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username, password=password)
            user.save()
            if not user:
                return Response(
                    {'error': 'Los datos de usuario no son válidos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'OK': 'Usuario registrado.'},
            status=status.HTTP_200_OK
        )


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        username = request.data.get("user")
        password = request.data.get("pass")
        if username is None:
            return Response(
                {'error': 'No se encontró el campo \'user\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif password is None:
            return Response(
                {'error': 'No se encontró el campo \'pass\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            user = authenticate(username=username, password=password)
            if not user:
                return Response(
                    {'error': 'Los datos de usuario no son válidos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })
