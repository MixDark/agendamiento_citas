"""
Script para agregar tokens CSRF a todos los formularios HTML.
Ejecutar una sola vez para actualizar todos los templates.
"""
import os
import re

# Directorio de templates
TEMPLATES_DIR = "app/templates"

# Archivos que ya tienen CSRF token
ALREADY_UPDATED = [
    "auth/login.html",
    "auth/register.html",
    "auth/change_password.html"
]

# Token CSRF a insertar
CSRF_TOKEN = '                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'

def add_csrf_to_file(filepath):
    """Agrega token CSRF a un archivo HTML si tiene formularios POST"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar formularios POST
    if '<form method="POST"' not in content and '<form method="post"' not in content:
        return False
    
    # Verificar si ya tiene token CSRF
    if 'csrf_token()' in content:
        print(f"✓ {filepath} ya tiene token CSRF")
        return False
    
    # Patron para encontrar la línea después de <form method="POST"...>
    pattern = r'(<form method="POST"[^>]*>)\s*\n'
    
    # Reemplazar agregando el token CSRF
    new_content = re.sub(
        pattern,
        r'\1\n' + CSRF_TOKEN + '\n',
        content,
        flags=re.IGNORECASE
    )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Token CSRF agregado a {filepath}")
        return True
    else:
        print(f"⚠ No se pudo agregar token CSRF a {filepath}")
        return False

def main():
    """Procesa todos los archivos HTML en el directorio de templates"""
    print("=" * 60)
    print("AGREGANDO TOKENS CSRF A FORMULARIOS")
    print("=" * 60)
    print()
    
    updated_count = 0
    
    # Recorrer todos los archivos HTML
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, TEMPLATES_DIR)
                
                # Saltar archivos ya actualizados
                if relative_path.replace('\\', '/') in ALREADY_UPDATED:
                    print(f"⊘ Saltando {relative_path} (ya actualizado)")
                    continue
                
                if add_csrf_to_file(filepath):
                    updated_count += 1
    
    print()
    print("=" * 60)
    print(f"Archivos actualizados: {updated_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
