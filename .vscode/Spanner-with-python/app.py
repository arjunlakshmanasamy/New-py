import os
from flask import Flask, jsonify, request
from google.cloud import spanner
from google.cloud.spanner_v1 import KeySet
from google.oauth2 import service_account

credentials_info = os.environ.get('SERVICE_ACCOUNT_KEY')
credentials = service_account.Credentials.from_service_account_info(credentials_info)
spanner_client = spanner.Client(credentials=credentials)
instance_id = 'your-instance-id'
database_id = 'your-database-id'
instance = spanner_client.instance(instance_id)
database = instance.database(database_id)

# Set up Flask  application
app = Flask(__name__)

@app.route('/health')
def health_check():
    try:       
        instance = spanner_client.instance('my-instance')
        database = instance.database('my-database')
        with database.snapshot() as snapshot:
            results = snapshot.execute_sql('SELECT 1')
        if results is not None:
            return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Define routes for CRUD operations
@app.route('/users', methods=['GET'])
def get_users():
    with database.snapshot() as snapshot:
        # Query users table and return JSON response
        rows = snapshot.execute_sql('SELECT * FROM users')
        users = [{'user_id': row[0], 'name': row[1], 'email': row[2], 'password': row[3]} for row in rows]
        return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with database.snapshot() as snapshot:
        # Query users table for user with given ID and return JSON response
        row = snapshot.execute_sql('SELECT * FROM users WHERE user_id = @user_id', params={'user_id': user_id}).single()
        if row is None:
            return jsonify({'error': 'User not found'}), 404
        user = {'user_id': row[0], 'name': row[1], 'email': row[2], 'password': row[3]}
        return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    with database.batch() as batch:
        # Insert new user into users table
        batch.insert(
            table='users',
            columns=('user_id', 'name', 'email', 'password'),
            values=[(user_id, name, email, password)]
        )
    return jsonify({'message': 'User created successfully'})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    with database.batch() as batch:
        # Update user with given ID in users table
        batch.update(
            table='users',
            columns=('user_id', 'name', 'email', 'password'),
            values=[(user_id, name, email, password)]
        )
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with database.batch() as batch:
        # Delete user with given ID from users table
        batch.delete(
            table='users',
            keyset=KeySet(keys=[[user_id]])
        )
    return jsonify({'message': 'User deleted successfully'})

# Start Flask application
if __name__ == '__main__':
    app.run()
