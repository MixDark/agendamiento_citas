"""
Script de producción multiplataforma para la aplicación de agendamiento de citas.
Detecta automáticamente el sistema operativo y usa el servidor apropiado:
- Windows: Waitress
- Linux/Mac: Gunicorn
"""
import os
import sys
import platform
import webbrowser
import threading
import time
from app import create_app

app = create_app()


def open_browser():
    """Función para abrir el navegador después de un pequeño retraso"""
    time.sleep(2)
    port = int(os.environ.get('PORT', 8000))
    webbrowser.open(f'http://localhost:{port}')


def run_with_waitress():
    """Ejecuta la aplicación usando Waitress (Windows)"""
    from waitress import serve
    
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    threads = int(os.environ.get('THREADS', 4))
    
    print(f"Iniciando servidor Waitress en {host}:{port}")
    
    # Abrir navegador automáticamente
    threading.Thread(target=open_browser, daemon=True).start()
    
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        url_scheme='http',
        channel_timeout=120,
        cleanup_interval=30,
        asyncore_use_poll=True
    )


def run_with_gunicorn():
    """Ejecuta la aplicación usando Gunicorn (Linux/Mac)"""
    import subprocess
    
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    workers = int(os.environ.get('WORKERS', os.cpu_count() * 2 + 1))
    
    print(f"Iniciando servidor Gunicorn en {host}:{port}")
    
    # Abrir navegador automáticamente
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Ejecutar Gunicorn
    cmd = [
        'gunicorn',
        '--bind', f'{host}:{port}',
        '--workers', str(workers),
        '--timeout', '120',
        'run:app'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nServidor detenido correctamente")


def main():
    """Función principal que detecta el SO y ejecuta el servidor apropiado"""
    sistema = platform.system()
        
    if sistema == 'Windows':
        run_with_waitress()
    else:
        try:
            run_with_gunicorn()
        except FileNotFoundError:
            print("Gunicorn no está instalado. Usando Waitress como alternativa")
            run_with_waitress()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServidor detenido correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\nError al iniciar el servidor: {e}")
        sys.exit(1)
