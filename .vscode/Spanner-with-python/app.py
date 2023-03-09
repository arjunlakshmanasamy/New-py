import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/keyfile.json'
from flask import Flask, request
from google.cloud import spanner

app = Flask(__name__)

# Set the Google Cloud Spanner instance and database name
instance_id = 'your-instance-id'
database_id = 'your-database-id'

# Create a Spanner client object
spanner_client = spanner.Client()

# Get a reference to the Cloud Spanner instance
instance = spanner_client.instance(instance_id)

# Get a reference to the Cloud Spanner database
database = instance.database(database_id)

# Define a Flask endpoint for creating a new row in the database
@app.route('/my_table', methods=['POST'])
def create_row():
    # Get the JSON data from the request body
    data = request.json

    # Create a new transaction
    with database.batch() as transaction:
        # Insert the data into the table
        row = (data['id'], data['name'])
        transaction.insert('my_table', [row])

    # Return a success response
    return {'status': 'success'}

# Define a Flask endpoint for reading all rows in the database
@app.route('/my_table', methods=['GET'])
def read_rows():
    # Create a new transaction
    with database.snapshot() as snapshot:
        # Execute a SQL statement to select all rows from the table
        results = snapshot.execute_sql('SELECT * FROM my_table')

        # Create a list of dictionaries representing each row
        rows = []
        for row in results:
            rows.append({'id': row[0], 'name': row[1]})

    # Return the list of rows as a JSON response
    return {'rows': rows}

# Define a Flask endpoint for reading a single row in the database
@app.route('/my_table/<int:id>', methods=['GET'])
def read_row(id):
    # Create a new transaction
    with database.snapshot() as snapshot:
        # Execute a SQL statement to select the row with the given ID
        params = {'id': id}
        results = snapshot.execute_sql('SELECT * FROM my_table WHERE id = @id', params)

        # If no row was found, return a 404 response
        row = next(results, None)
        if row is None:
            return {'status': 'error', 'message': f'Row with ID {id} not found'}, 404

        # Return the row as a JSON response
        return {'id': row[0], 'name': row[1]}

# Define a Flask endpoint for updating a row in the database
@app.route('/my_table/<int:id>', methods=['PUT'])
def update_row(id):
    # Get the JSON data from the request body
    data = request.json

    # Create a new transaction
    with database.batch() as transaction:
        # Execute a SQL statement to update the row with the given ID
        params = {'id': id, 'name': data['name']}
        transaction.execute_update('UPDATE my_table SET name = @name WHERE id = @id', params)

    # Return a success response
    return {'status': 'success'}



