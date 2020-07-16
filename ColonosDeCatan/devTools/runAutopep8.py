import os

cmd = 'autopep8 --in-place --aggressive --aggressive'
path = os.path.dirname(__file__)
pathapi = os.path.join(path, '../API/')
data = os.path.join(path, 'data.py')
all = os.path.join(path, 'all.py')


os.system('{} {}'.format(cmd, data))
os.system('{} {}'.format(cmd, all))
os.system('{} {}Board/*.py'.format(cmd, pathapi))
os.system('{} {}Games/*.py'.format(cmd, pathapi))
os.system('{} {}PlayerInfo/*.py'.format(cmd, pathapi))
os.system('{} {}Room/*.py'.format(cmd, pathapi))
os.system('{} {}Transaction/*.py'.format(cmd, pathapi))
os.system('{} {}User/*.py'.format(cmd, pathapi))
print('Finalizado todas las pepocheadas')
