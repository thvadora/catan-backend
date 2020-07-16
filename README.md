Proyecto Catan
==

## Ingenieria de Software I: 2019

### Backend de una API REST

### Alumnos:
  * __Balog Santiago Alberto__ (@00santiagob) ~ _santiagobalog1998@gmail.com_
  * __Farias Guillermo Joel__ (@joelfarias999) ~ _joelfarias999@gmail.com_
  * __González Kriegel Federico__ (@FedeKriegel) ~ _fedekriegel@gmail.com_
  * __Piatti Mariano__ (@marianopiatti) ~ _marianopiatti@gmail.com_
  * __Vadora Thomas__ (@thvadora) ~ _thvadora@gmail.com_

## Resumen

 El Proyecto __Colonos de Catan__ es una implementación de una API REST para el servicio del juego __Los Colonos de Catan__ (_Settlers of Catan_). En esta API los jugadores pueden registrarse, loguearse, unirse a diferentes partidas, ver sus cartas de recursos y de desarrollo, jugar sus cartas, etc. como en el juego original (a excepcion de algunos cambios).

El backend esta implementado en [Django](https://www.djangoproject.com/), un framework del lenguaje de programacion Python, en su version [Django REST framework](https://www.django-rest-framework.org/): un potente y flexible conjunto de herramientas para la creacion de APIs Webs.

## Configuración Manual

Para empezar a usar la API se debe clonar el repositorio:

    $ git clone https://gitlab.com/p-np-cuando-n-1/catan.git

### Pre-Requisitos (Instalación)
> **Nota:**
> Se recomienda hacer `sudo apt update && sudo apt upgrade` antes de instalar todos los siguientes requisitos.

Tener instalado __Python__:
    
    $ sudo apt install python3-pip

> **Nota:**
> La instalacion de Python en __macOS__ es: `$ brew install python3`

También se usara la herramienta de entorno virtual:

    $ sudo apt install python3-venv

### Como ejecutar el Repositorio

Una vez hecho lo anterior, se debe ingresar a la carpeta del repositorio:

    $ cd catan/

Ya dentro se debe crear un entorno virtual y luego ingresar a él:

    $ python3 -m venv env
    $ source env/bin/activate

Entramos a la carpeta del proyecto __ColonosDeCatan__:

    $ cd ColonosDeCatan/

Y dentro de la carpeta __ColonosDeCatan__ se debe actualizar la herramienta __pip__ e instalar requerimientos para la API :

    $ pip install pip --upgrade
    $ pip install setuptools --upgrade
    $ pip install -r requirements.txt
    
Luego se deben ejecutar los comandos:

    $ python3 devTools/migrate.py
   
Y finalmente correr la API con los comandos:
    
    $ python3 manage.py runserver

> **Nota:**
> El puerto por defecto en que se conecta es: 8000
> Si se quiere cambiar el puerto en que se conecta la API se lo puede especificar de esta forma: `$ python manage.py runserver <puerto>`

### Como correr los Tests
Para correr los tests de cada paquete primero se debe ir a la carpeta API:

    $ cd catan/ColonosDeCatan/API
    
Y luego para ejecutar los tests de un paquete en particular se ejecuta:

    $ python3 ../manage.py test <Nombre del paquete>

Por ejemplo si se quiere testear el paquete Room se ejecuta:

    $ python3 ../manage.py test Room

Si se quiere ejecutar todos los tests, en la carpeta ColonosDeCatan, hacer:

    $ python3 manage.py test
    
### Estructura del Proyecto

      catan
         |
         |__ /ColonosDeCatan
         |    |
         |    |__ /API
         |    |     |__ __init__.py
         |    |     |_ /Board
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |     |_ /Games
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |     |_ /PlayerInfo
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |     |_ /Room
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |     |_ /Transaction
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |     |_ /User
         |    |     |    |__ __init__.py
         |    |     |    |__ admin.py
         |    |     |    |__ apps.py
         |    |     |    |__ models.py
         |    |     |    |__ serializers.py
         |    |     |    |__ test_no_existentes.txt
         |    |     |    |__ test_superusers.txt
         |    |     |    |__ test_users.txt
         |    |     |    |__ tests.py
         |    |     |    |__ Views.py
         |    |
         |    |__ /ColonosDeCatan
         |    |     |__ __init__.py
         |    |     |__ settings.py
         |    |     |__ urls.py
         |    |     |__ wsgi.py
         |    |__ manage.py
         |    |__ requirements.txt
         |
         |__ .gitignore
         |__ README.md