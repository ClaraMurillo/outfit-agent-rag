import sqlite3
import os

os.makedirs("data", exist_ok=True)

# 1. Base de datos estructurada (Stock, talles y precios)
conn = sqlite3.connect("data/catalogo.db")
cursor = conn.cursor()

# Limpiar tabla si existe para poder correr el script varias veces sin duplicar
cursor.execute('DROP TABLE IF EXISTS inventario')

cursor.execute('''
CREATE TABLE inventario (
    id_producto TEXT,
    tipo TEXT,
    color TEXT,
    talle TEXT,
    precio REAL,
    stock INTEGER
)
''')

# Insertar datos de prueba (MVP)
# Nota: El S-001 en talle L tiene 0 stock a propósito para probar el caso de restricción incumplida.
productos = [
    ("S-001", "saco", "azul marino", "M", 150.0, 5),
    ("S-001", "saco", "azul marino", "L", 150.0, 0),
    ("S-002", "saco", "gris", "M", 120.0, 2),
    ("C-001", "camisa", "blanca", "M", 50.0, 10),
    ("C-001", "camisa", "blanca", "L", 50.0, 5),
    ("V-001", "vestido", "negro", "S", 200.0, 3)
]
cursor.executemany('INSERT INTO inventario VALUES (?,?,?,?,?,?)', productos)
conn.commit()
conn.close()

# 2. Base de conocimientos inestructurada (Reglas de estilo para el RAG)
reglas_estilo = """
Guía de estilo para eventos:
- Casamiento de noche o gala: Se recomiendan sacos oscuros (azul marino, negro). El producto S-001 es ideal.
- Casamiento de día: Se recomiendan colores claros como el gris (S-002).
- Cóctel formal: El vestido negro (V-001) es un clásico infalible.
- Combinaciones: Un saco azul marino combina perfectamente con un pantalón negro o gris. Una camisa blanca (C-001) va con todo.
"""

with open("data/guias_estilo.txt", "w", encoding="utf-8") as f:
    f.write(reglas_estilo)

print("Datos simulados creados con éxito en la carpeta /data.")
