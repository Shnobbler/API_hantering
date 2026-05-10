from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'inlamning1' # Ändra namnet så det passar din databasserver
}

def get_db_connection():
    """Get a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    return ''' <h1>Välkommen till min API!</h1>
    <h2>ROUTES: </h2>
    <ul>
        <li> GET /users - hämta alla users - kräver inloggning (token)</li>
        <li> GET /users/&lt;id eller username&gt; - hämta user med id eller username - kräver inloggning (token)</li>
        <li> POST /users - skapa en user - kräver inloggning (token)</li>
        <li> POST /login - logga in och få en token </li>
        <li> POST /register - registrera en ny user </li>
        <li> PUT /users/&lt;id&gt; - uppdatera user med id - kräver inloggning (token)</li>
        <li> DELETE /users/&lt;id&gt; - ta bort user med id - kräver inloggning (token)</li>
        <li> GET /protected - skyddad route - kräver inloggning (token)</li>
    </ul>
'''

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    sql = "SELECT id, username, email, name FROM users"
    cursor.execute(sql)
    users = cursor.fetchall()

    if not users:
        return jsonify({"error": "User not found"}), 404
    
    connection.close()
    return jsonify(users)

# @app.route('/users', methods=['GET'])
# def get_users():
#     users = [
#         {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
#         {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
#         {'id': 3, 'name': 'Carol', 'email': 'carol@example.com'}
#     ]
#     return jsonify(users)

@app.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get all users"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    # hämta ENDAST user med id
    sql = "SELECT id, username, email, name FROM users WHERE id = %s OR username = %s"
    cursor.execute(sql, (user_id, user_id))
    user = cursor.fetchone()

    connection.close()

    if not user:
        return jsonify({"error": "User not found"}), 404
   
    return jsonify(user)


@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user"""
    data = request.get_json(silent=True)  # Hämta data från requesten.
    

    try:
        if data and 'username' in data and 'password' in data and 'email' in data and 'name' in data: # Verifierar att username skickats
            username = data.get('username')
            password = data.get('password')
            hashed_password = generate_password_hash(password)
            email = data.get('email')
            name = data.get('name')
            connection = get_db_connection()
            
            cursor = connection.cursor()
            sql = "INSERT INTO users (username, password, email, name) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, email, name ))
                
            connection.commit() # commit() gör klart skrivningen till databasen
            user_id = cursor.lastrowid # cursor.lastrowid innehåller id på raden som skapades i DB
                
            # user = {
            # 'id': user_id,
            # 'username': username,
            # 'passoword': password,
            # 'email': email,
            # 'name': name
            # }
            return jsonify({
                "id": user_id,
                "username": username,
                "email": email,
                "name": name
            }), 201
        else:
            # Returnera ett JSON-objekt med felmeddelandet och statuskod 422
            return jsonify({"error": "Sum Ting Wong, Ho Lee Fuk"}), 422
    
    except Exception as err:
        print(f"Error: {err}")
        return jsonify({"error": "Something went wrong. Sorry!"}), 500

    
# @app.route('/users/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     return jsonify(user_id)

@app.route('/user', methods=['GET'])
def get_username():
    username = request.args.get('username', '')
    return jsonify({'username': username})

@app.route('/hash', methods=['GET'])
def get_hash():
    passw = request.args.get('password', '')
    return generate_password_hash(passw)

@app.route('/cars', methods=['GET'])
def get_cars():
    cars = [
        {'make': 'Mercedes', 'model': 'S220d', 'year': '2005'},
        {'make': 'BMW', 'model': '330e', 'year': '2021'},
        {'make': 'Volvo', 'model': 'EX60', 'year': '2026'}
    ]
    return jsonify(cars)

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor(dictionary=True)
            # 1. Hämta data från body (req.body)
        data = request.get_json(silent=True)
        print(f"Recieved data: {data}")
            #lägg till verifiering av data här vid behov, skicka t.ex. status 400
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')            # skapa databaskoppling (kod bortklippt) och använd UPDATE för att uppdatera databasen

        if not username or not password or not email or not name:
            return jsonify({"error": "Alla fält måste skickas med"}), 400
        
        hashed_password = generate_password_hash(password)

        sql = """UPDATE users SET username = %s, password = %s, email = %s, name = %s WHERE id = %s"""
        
            # 3. Kör frågan med en tupel av värden
        cursor.execute(sql, (username, hashed_password, email, name, user_id))
    
        connection.commit()
        if cursor.rowcount == 0:
            connection.close()
            return jsonify({"error": "Användaren hittades inte"}), 404

        sql_select = "SELECT id, username, email, name FROM users WHERE id = %s"
        cursor.execute(sql_select, (user_id,))
        updated_user = cursor.fetchone()

        connection.close()

        return jsonify(updated_user), 200

    except Exception as err:
        print(f"Error: {err}")
        return jsonify({"error": "Something went wrong. Sorry!"}), 500
    
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor()

        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        connection.commit()

        if cursor.rowcount == 0:
            connection.close()
            return jsonify({"error": "User not found"}), 404

        connection.close()
        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as err:
        print(f"Error: {err}")
        return jsonify({"error": "Something went wrong. Sorry!"}), 500
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if user already exists
        sql_check = "SELECT id FROM users WHERE username = %s"
        cursor.execute(sql_check, (username,))
        if cursor.fetchone():
            return jsonify({'error': 'User already exists'}), 409
        
        # Insert new user
        sql_insert = "INSERT INTO users (username, password, email, name) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert, (username, hashed_password, email, name))
        connection.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Failed to create user'}), 500
    
    finally:
        if connection:
            connection.close()

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    print(get_jwt())
    return jsonify(logged_in_as=current_user), 200

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    user_name = data.get('username')
    password = data.get('password')
   
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
       
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (user_name,))
    user = cursor.fetchone()

   
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    access_token = create_access_token(identity=user_name)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)