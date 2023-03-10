import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/keyfile.json'
from flask import Flask, jsonify, request
from google.cloud import spanner
from google.cloud.spanner_v1 import KeySet

app = Flask(__name__)
instance_id = 'your-instance-id'
database_id = 'your-database-id'
client = spanner.Client()
instance = client.instance(instance_id)
database = instance.database(database_id)

# Define the users table name and columns
users_table = 'users'
users_columns = ['user_id', 'name', 'email', 'password']

# API endpoint to get all users
@app.route('/users', methods=['GET'])
def get_users():
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(f'SELECT * FROM {users_table}')
        users = [dict(zip(users_columns, row)) for row in results]
        return jsonify(users)

# API endpoint to get a specific user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(f'SELECT * FROM {users_table} WHERE user_id = @user_id', params={'user_id': user_id})
        row = list(results)
        if len(row) > 0:
            user = dict(zip(users_columns, row[0]))
            return jsonify(user)
        else:
            return f'User with ID {user_id} not found', 404

# API endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    user = request.get_json()
    if not all(key in user for key in users_columns[1:]):
        return 'Missing fields in request body', 400
    with database.batch() as batch:
        batch.insert(
            table=users_table,
            columns=users_columns[1:],
            values=[(user['name'], user['email'], user['password'])]
        )
    return 'User created successfully', 201

# API endpoint to update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = request.get_json()
    if not all(key in user for key in users_columns[1:]):
        return 'Missing fields in request body', 400
    with database.batch() as batch:
        batch.update(
            table=users_table,
            columns=users_columns[1:],
            values=[(user['name'], user['email'], user['password'])],
            keyset=KeySet(keys=[(user_id,)]),
        )
    return 'User updated successfully', 200



