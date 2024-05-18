import sys
import psutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.core.management import call_command
from django.contrib.staticfiles import finders
import os
from multiprocessing import Process
from . import settings

def get_project_name():
    settings_module = os.getenv('DJANGO_SETTINGS_MODULE')
    if settings_module is not None:
        project_name = settings_module.split('.')[0]
        return project_name
    else:
        return None

def kill_gunicorn():
    for process in psutil.process_iter():
        if 'gunicorn' in process.name():
            process.kill()

def run_gunicorn_http(hostname=None, port=None):
    hostname = hostname or settings.SMARTWATCH_HTTP_HOST
    port = port or settings.SMARTWATCH_HTTP_PORT
    kill_gunicorn()
    os.system(f'gunicorn -b {hostname}:{port} {get_project_name()}.wsgi:application')


def kill_daphne():
    for process in psutil.process_iter():
        if 'daphne' in process.name():
            process.kill()


def run_daphne_ws(hostname=None, port=None):
    hostname = hostname or settings.SMARTWATCH_WS_HOST
    port = port or settings.SMARTWATCH_WS_PORT
    kill_daphne()
    os.system(f'daphne -b {hostname} -p {port} {get_project_name()}.asgi:application')


def start_servers():
    Process(target=run_gunicorn_http).start()
    # Process(target=run_daphne_ws).start()
    print('started the servers')


class ServerHandler(FileSystemEventHandler):
    def on_modified(self, event):
        should_restart = event.src_path.endswith('.py')
        if event.src_path == 'requirements.txt':
            logging.info(f'{event.src_path} has been modified. Installing requirements...')
            should_restart = True
            os.system('pip install -r requirements.txt')
        if settings.SMARTWATCH_MIGRATE and 'migrations' in event.src_path:
            should_restart = False
            logging.info(f'{event.src_path} has been modified. Running migrations...')
            call_command('migrate')
        if settings.SMARTWATCH_COLLECT_STATIC and 'static' in event.src_path:
            logging.info(f'{event.src_path} has been modified. Collecting static files...')
            call_command('collectstatic', '--noinput')
        if should_restart:
            logging.info(f'{event.src_path} has been modified. Restarting server...')
            start_servers()


def watch_files():
    server_handler = ServerHandler()
    observer = Observer()
    observer.schedule(server_handler, '.', recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
