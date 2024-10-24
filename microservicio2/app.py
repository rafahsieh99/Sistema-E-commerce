from flask import Flask, request, jsonify
import requests
from datetime import datetime
from db import get_db_connection

app = Flask(__name__)

# URL del microservicio de productos
PRODUCTO_SERVICE_URL = 'http://localhost:5001/productos/'

# Agregar producto al carrito
@app.route('/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    try:
        data = request.get_json()
        username = data.get('username')
        product_id = data.get('product_id')
        cantidad = data.get('cantidad', 1)

        # Validación de datos
        if not username or not product_id:
            return jsonify({"mensaje": "Username y product_id son requeridos"}), 400

        # Consultar el microservicio de productos para verificar si el producto existe
        producto_response = requests.get(f"{PRODUCTO_SERVICE_URL}{product_id}")

        if producto_response.status_code != 200:
            return jsonify({"mensaje": "Producto no encontrado", "error": producto_response.text}), 404

        # Obtener la fecha y hora actuales
        fecha_agregado = datetime.now()

        # Si el producto existe, proceder a agregarlo al carrito
        conn = get_db_connection()
        cursor = conn.cursor()

        # Comprobar si el producto ya está en el carrito
        cursor.execute("""
            SELECT * FROM carritos WHERE username = %s AND product_id = %s;
        """, (username, product_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Si ya existe, actualizar la cantidad
            new_cantidad = existing_item[2] + cantidad  # Suponiendo que 'cantidad' es la tercera columna
            cursor.execute("""
                UPDATE carritos SET cantidad = %s, fecha_agregado = %s WHERE username = %s AND product_id = %s;
            """, (new_cantidad, fecha_agregado, username, product_id))
        else:
            # Si no existe, insertar un nuevo registro
            cursor.execute("""
                INSERT INTO carritos (username, product_id, cantidad, fecha_agregado) VALUES (%s, %s, %s, %s);
            """, (username, product_id, cantidad, fecha_agregado))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Producto agregado al carrito con éxito", "fecha_agregado": fecha_agregado.isoformat()}), 201

    except Exception as e:
        return jsonify({"mensaje": "Error al agregar producto al carrito", "error": str(e)}), 500

# Modificar cantidad de producto en el carrito
@app.route('/carrito/modificar', methods=['PUT'])
def modificar_carrito():
    try:
        data = request.get_json()
        username = data['username']
        product_id = data['product_id']
        cantidad = data['cantidad']

        if not username or not product_id or cantidad is None:
            return jsonify({"mensaje": "Username, product_id y cantidad son requeridos"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE carritos
            SET cantidad = %s
            WHERE username = %s AND product_id = %s;
        """, (cantidad, username, product_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el producto en el carrito para modificar."}), 404

        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Carrito modificado con éxito!"}), 200

    except Exception as e:
        return jsonify({"mensaje": "Error al modificar carrito", "error": str(e)}), 500

# Eliminar producto del carrito
@app.route('/carrito/eliminar', methods=['DELETE'])
def eliminar_del_carrito():
    try:
        data = request.get_json()
        username = data['username']
        product_id = data['product_id']

        if not username or not product_id:
            return jsonify({"mensaje": "Username y product_id son requeridos"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM carritos
            WHERE username = %s AND product_id = %s;
        """, (username, product_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"mensaje": "No se encontró el producto en el carrito para eliminar."}), 404

        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Producto eliminado del carrito!"}), 200

    except Exception as e:
        return jsonify({"mensaje": "Error al eliminar producto del carrito", "error": str(e)}), 500

# Obtener productos del carrito
@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    try:
        username = request.args.get('username')

        if not username:
            return jsonify({"mensaje": "Username es requerido"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, product_id, cantidad, fecha_agregado FROM carritos WHERE username = %s;
        """, (username,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()

        # Crear una lista de diccionarios para retornar con nombres de columnas
        columnas = ['username', 'product_id', 'cantidad', 'fecha_agregado']
        resultado = [dict(zip(columnas, item)) for item in items]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"mensaje": "Error al obtener el carrito", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)  # Cambia el puerto si es necesario
