from app import create_app
import webbrowser
import threading
import time
import os

app = create_app()


def open_browser():
    """Función para abrir el navegador después de un pequeño retraso"""
    time.sleep(1.5)  # Espera 1.5 segundos para asegurar que el servidor esté listo
    port = int(os.environ.get('PORT', 8000))
    webbrowser.open(f'http://localhost:{port}')


if __name__ == '__main__':
    # Inicia un thread para abrir el navegador
    threading.Thread(target=open_browser, daemon=True).start()

    # Inicia el servidor de desarrollo de Flask
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
