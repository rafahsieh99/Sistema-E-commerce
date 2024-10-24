from flask import Flask, request, jsonify
import psycopg2
from db import get_db_connection

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="producto",
        user="postgres",
        password="123456"
    )
    return conn

# Obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos;')
    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(productos), 200

# Obtener un producto específico (ID)
@app.route('/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE product_id = %s;', (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    if producto is None:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

    return jsonify(producto), 200

# Crear un nuevo producto
@app.route('/productos', methods=['POST'])
def crear_producto():
    data = request.get_json()
    nombre_pro = data['nombre_pro']
    descri_pro = data['descri_pro']
    precio_pro = data['precio_pro']
    categoria_pro = data['categoria_pro']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO productos (nombre_pro, descri_pro, precio_pro, categoria_pro) VALUES (%s, %s, %s, %s) RETURNING *;',
        (nombre_pro, descri_pro, precio_pro, categoria_pro)
    )
    nuevo_producto = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Producto creado", "producto": nuevo_producto}), 201

# Actualizar un producto
@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    data = request.get_json()
    nombre_pro = data['nombre_pro']
    descri_pro = data['descri_pro']
    precio_pro = data['precio_pro']
    categoria_pro = data['categoria_pro']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE productos SET nombre_pro = %s, descri_pro = %s, precio_pro = %s, categoria_pro = %s WHERE product_id = %s RETURNING *;',
        (nombre_pro, descri_pro, precio_pro, categoria_pro, id)
    )
    actualizado = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if actualizado is None:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

    return jsonify({"mensaje": "Producto actualizado", "producto": actualizado}), 200

# Eliminar un producto
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE product_id = %s;', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

    return jsonify({"mensaje": "Producto eliminado"}), 200

if __name__ == '__main__':
    app.run(port=5001)
