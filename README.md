# Django Django REST Framework

Proyecto con Django y DRF, Celery y Redis para la gestión de tareas asincrónicas.

## Configuración

Instrucciones:

```bash
# entorno virtual
python -m venv venv

# gnu/linux - mac
source venv/bin/activate

# windows
venv/script/activate

# instala las dependencias
pip install -r requirements.txt
```

## Ejecuta el proyecto

Copia las variables de entorno a un .env como el .env.example. A continuación:

```bash
# crea las migraciones
python manage.py makemigrations

# ejecuta las migraciones
python manage.py migrate

# crea un usuario administrador
python manage.py createsuperuser

# ejecuta el proyecto
python manage.py runserver
```

## Docker para Redis

Crea un contenedor de redis

```bash
# crear y levanta un contenedor docker de redis
docker run --name redis-container -p 6379:6379 -d redis
```

## Celery

Ejecuta celery:

```bash
# ejecuta flower para visualizar las tareas en http://localhost:5555/
celery -A main.celery_app flower

# ejecuta celery
celery -A main worker --loglevel=debug
```
