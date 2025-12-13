"""
Script para generar una SECRET_KEY criptográficamente segura.
Ejecuta este script y copia el resultado a tu archivo .env
"""
import secrets

print("=" * 60)
print("GENERADOR DE SECRET_KEY SEGURA")
print("=" * 60)
print()
print("Copia la siguiente clave y pégala en tu archivo .env:\n")
print(f"SECRET_KEY={secrets.token_hex(32)}\n")
print("""IMPORTANTE:
Esta clave es única y criptográficamente segura
Cambiar esta clave invalidará todas las sesiones activas
NUNCA compartas esta clave públicamente
Guárdala de forma segura""")
print("=" * 60)
