import os
path = os.path.dirname(__file__)
path = os.path.join(path, '../manage.py')

os.system('python3 {} makemigrations Board'.format(path))
os.system('python3 {} makemigrations Games'.format(path))
os.system('python3 {} makemigrations PlayerInfo'.format(path))
os.system('python3 {} makemigrations Room'.format(path))
os.system('python3 {} makemigrations User'.format(path))
os.system('python3 {} makemigrations Transaction'.format(path))
os.system('python3 {} migrate'.format(path))
print('Finalizado las migraciones')
