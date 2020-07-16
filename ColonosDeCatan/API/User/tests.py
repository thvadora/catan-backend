from django.test import TestCase, Client
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

import os
TEST_USERS = os.path.join(os.path.dirname(__file__), 'test_users.txt')
TEST_SUPERUSERS = os.path.join(
    os.path.dirname(__file__),
    'test_superusers.txt')
TEST_USERS_NO_EXISTENTES = os.path.join(
    os.path.dirname(__file__),
    'test_no_existentes.txt')

# Database
USERS_OK = [
    {"user": "00sb", "pass": "kelokeEsto"},
    {"user": "pacoPerfum", "pass": "yEstoQes"},
    {"user": "admin", "pass": "admin-admin"},
    {"user": "ingenieria", "pass": "ingenieria"}
]

USERS_EMPTY_USER = [
    {"pass": "kelokeEsto"},
    {"user": "", "pass": "yEstoQes"},
    {"user": "   ", "pass": "admin-admin"},
    {"user": "  algoUserr", "pass": "ingenieria"}
]

USERS_EMPTY_PASS = [
    {"user": "00santiagob"},
    {"user": "paquito", "pass": ""},
    {"user": "root", "pass": "   "},
    {"user": "ing", "pass": "esto no anda"},
    {"user": "pocoCaracter", "pass": "CasiJaa"}
]

USERS_ALREADY_EXIST = [
    {"user": "00sb", "pass": "kelokeEsto"},
    {"user": "pacoPerfum", "pass": "yEstoQes"},
    {"user": "admin", "pass": "admin"},
    {"user": "ingenieria", "pass": "ingenieria"}
]


class RegisterUserTest(TestCase):

    def testSignUp_Ok(self):
        print('Registracion de usuarios exitosos:')
        client = Client()
        for user in USERS_OK:
            response = client.post(
                '/users/', user, content_type='application/json')
            self.assertEqual(response.status_code, 200)
        print('-OK-')

    def testSignUp_EmptyUser(self):
        print('Error de registracion de usuarios sin username:')
        client = Client()
        for user in USERS_EMPTY_USER:
            response = client.post(
                '/users/', user, content_type='application/json')
            self.assertEqual(response.status_code, 400)
        print('-OK-')
        pass

    def test_SignUp_AlreadyExist(self):
        print('Intentos fallidos de registrar usuarios existentes:')
        client = Client()
        for user in USERS_OK:
            user = User.objects.create_user(
                username=user['user'], password=user['pass'])
            user.save()
        for user in USERS_ALREADY_EXIST:
            response = client.post(
                '/users/', user, content_type='application/json')
            self.assertEqual(response.status_code, 400)
        print('-OK-')
        pass


class testUsers(TestCase):
    def setUp(self):
        count = 1
        f = open(TEST_USERS)
        while True:
            username = f.readline()
            password = f.readline()
            if not password:
                break
            new_user = User(username=username, password=password)
            new_user.save()
            count = count + 1
        print('Cargando de Users OK')
        f.close()

    def test(self):
        c = Client()
        f = open(TEST_USERS)
        count = 1
        while True:
            username = f.readline()
            password = f.readline()
            if not password:
                break
            response = c.post(
                '/users/login/', {'user': username, 'pass': password}).json()
            self.assertTrue('token' in response)
            response = c.get(
                '/boards',
                HTTP_AUTHORIZATION='Token {}'.format(
                    response['token']))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, [])
            count = count + 1
        print(
            'Test devolución de token para User creado',
            'y utilización de token : OK')
        f.close()


class testSuperUsers(TestCase):
    def setUp(self):
        f = open(TEST_SUPERUSERS)
        count = 1
        while True:
            username = f.readline()
            password = f.readline()
            if not password:
                break
            new_user = User(username=username, password=password)
            new_user.is_staff = True
            new_user.is_admin = True
            try:
                with transaction.atomic():
                    new_user.save()
            except IntegrityError:
                pass
            count = count + 1
        print('Cargado de SuperUsers : OK')
        f.close()

    def test(self):
        c = Client()
        f = open(TEST_SUPERUSERS)
        count = 1
        while True:
            username = f.readline()
            password = f.readline()
            if not password:
                break
            response = c.post(
                '/users/login/', {'user': username, 'pass': password}).json()
            self.assertTrue('token' in response)
            response = c.get(
                '/boards',
                HTTP_AUTHORIZATION='Token {}'.format(
                    response['token']))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, [])
            count = count + 1
        print(
            'Test devolución de token para SuperUser creado',
            'y utilización de token : OK')
        f.close()


class testUsersNoExistentes(TestCase):
    def test(self):
        c = Client()
        f = open(TEST_USERS_NO_EXISTENTES)
        count = 1
        while True:
            username = f.readline()
            password = f.readline()
            if not password:
                break
            response = c.post(
                '/users/login/', {'user': username, 'pass': password}).json()
            self.assertTrue('token' not in response)
            count = count + 1
        print(
            'Test de devolución de error para Users inexistentes: OK')
        f.close()


class testBordes(TestCase):
    def setUp(self):
        self.c = Client()
        new_user = User(username='test', password='test123')
        new_user.save()

    def test_SinPassword(self):
        caso_borde = {
            'user': 'hola'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertTrue('error' in response)
        self.assertEqual(
            response['error'],
            'No se encontró el campo \'pass\'.')
        print('Test de caso borde : POST sin password : OK')

    def test_SinUsername(self):
        caso_borde = {
            'pass': 'hola'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertTrue('error' in response)
        self.assertEqual(
            response['error'],
            'No se encontró el campo \'user\'.')
        print('Test de caso borde : POST sin username : OK')

    def test_MuchosParams(self):
        caso_borde = {
            'user': 'test',
            'pass': 'test123',
            'campoadicional': 'paratesteo'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue('token' in response)
        print('Test de caso borde : POST con parametro de más : OK')

    def test_UsernameMalEscrito(self):
        caso_borde = {
            'usr': 'test',
            'pass': 'test123'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertTrue('error' in response)
        self.assertEqual(
            response['error'],
            'No se encontró el campo \'user\'.')
        print('Test de caso borde : POST con username mal escrito : OK')

    def test_PasswordMalEscrito(self):
        caso_borde = {
            'user': 'test',
            'pas': 'test123'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertTrue('error' in response)
        self.assertEqual(
            response['error'],
            'No se encontró el campo \'pass\'.')
        print('Test de caso borde : POST con password mal escrito : OK')

    def test_AmbosMalEscritos(self):
        caso_borde = {
            'usr': 'test',
            'pas': 'test123'
        }
        response = self.c.post('/users/login/', caso_borde)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertTrue('error' in response)
        self.assertEqual(
            response['error'],
            'No se encontró el campo \'user\'.')
        print('Test de caso borde:',
              'POST con username y password mal escritos : OK')
