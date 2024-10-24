from flask import Flask, request, jsonify
from db import get_db_connection  # Asegúrate de que la conexión a la base de datos esté correctamente importada
from datetime import datetime  # Importar datetime para generar la fecha de compra automáticamente
import requests

app = Flask(__name__)
# Ruta para crear un pedido
@app.route('/pedidos', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    username = data['username']
    product_id = data['product_id']
    cantidad = data['cantidad']
    estado = data['estado']

    # Verificar si el product_id existe en el microservicio de carrito
    respuesta_carrito = requests.get(f'http://127.0.0.1:5000/carrito?username={username}')
    if respuesta_carrito.status_code != 200:
        return jsonify({"error": "No se pudo obtener el carrito del usuario"}), 404

    items_carrito = respuesta_carrito.json()

    # Verificar si el product_id está en el carrito
    if not any(item['product_id'] == product_id for item in items_carrito):
        return jsonify({"error": "El product_id no existe en el carrito"}), 404

    # Generar automáticamente la fecha de compra
    fecha_compra = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO pedidos (username, product_id, cantidad, estado, fecha_compra)
                    VALUES (%s, %s, %s, %s, %s);""",
                (username, product_id, cantidad, estado, fecha_compra))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Pedido creado exitosamente"}), 201


# Ruta para obtener todos los pedidos
@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos;")
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()

    # Para dar formato a la respuesta de los pedidos
    return jsonify([{
        "order_id": pedido[0],  # Cambiar "id" por "order_id"
        "username": pedido[1],
        "product_id": pedido[2],
        "cantidad": pedido[3],
        "estado": pedido[4],
        "fecha_compra": pedido[5]
    } for pedido in pedidos]), 200

# Ruta para obtener un pedido específico
@app.route('/pedidos/<int:order_id>', methods=['GET'])
def obtener_pedido(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE order_id = %s;", (order_id,))  # Cambiar "id" por "order_id"
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()

    if pedido:
        return jsonify({
            "order_id": pedido[0],  # Cambiar "id" por "order_id"
            "username": pedido[1],
            "product_id": pedido[2],
            "cantidad": pedido[3],
            "estado": pedido[4],
            "fecha_compra": pedido[5]
        }), 200
    else:
        return jsonify({"error": "Pedido no encontrado"}), 404

# Ruta para actualizar un pedido
@app.route('/pedidos/<int:order_id>', methods=['PUT'])
def actualizar_pedido(order_id):
    data = request.get_json()
    username = data.get('username')
    cantidad = data.get('cantidad')
    estado = data.get('estado')


    conn = get_db_connection()
    cursor = conn.cursor()

    # Actualiza solo los campos que se proporcionen
    if username:
        cursor.execute("UPDATE pedidos SET username = %s WHERE order_id = %s;", (username, order_id))  # Cambiar "id" por "order_id"
    if cantidad is not None:
        cursor.execute("UPDATE pedidos SET cantidad = %s WHERE order_id = %s;", (cantidad, order_id))  # Cambiar "id" por "order_id"
    if estado:
        cursor.execute("UPDATE pedidos SET estado = %s WHERE order_id = %s;", (estado, order_id))  # Cambiar "id" por "order_id"

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Pedido actualizado exitosamente"}), 200

# Ruta para eliminar un pedido
@app.route('/pedidos/<int:order_id>', methods=['DELETE'])
def eliminar_pedido(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE order_id = %s;", (order_id,))  # Cambiar "id" por "order_id"
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Pedido eliminado exitosamente"}), 200

if __name__ == '__main__':
    app.run(port=5002)