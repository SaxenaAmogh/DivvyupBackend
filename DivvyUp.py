from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv


app = Flask(__name__)
mysql = MySQL(app)
load_dotenv()

app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']

@app.route('/divvyup/signup', methods=['POST'])
def add_user():
    try:

        if not request.is_json:
            return jsonify({'message': 'Unsupported Media Type: Expected JSON'}), 415
        
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users(username, email, password) VALUES(%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'User added successfully'}), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/divvyup/users', methods=['GET'])
def get_users():
    try:
        # Get email from query parameters
        email = request.args.get('email')
        print(email)
        if not email:
            return jsonify({'message': 'Email not provided'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print(user[0])
            return jsonify(user[0]), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/divvyup/profile', methods=['GET'])
def get_profile():
    try:
        # Get email from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'Email not provided'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return jsonify({'username': user[1], 'email': user[2], 'expense':user[4]}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/divvyup/expense', methods=['GET'])
def get_expense():
    try:
        # Get email from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'Email not provided'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print(user[4])
            return jsonify(user[4]), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/divvyup/friends', methods=['GET'])
def get_friends():
    try:
        # Get email from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'Email not provided'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM friends WHERE user_id = %s', (user_id,))
        all_friends = cursor.fetchall()
        friend = ""
        friend_num = 0
        cursor.close()
        for x in all_friends:
            friend += x[2] + " "
            friend_num += 1

        if all_friends:
            return jsonify({'friends': friend, 'friend_num': friend_num}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/addBill', methods=['POST'])
def add_bill():
    data = request.get_json()

    user_id = data.get('user_id')
    friends = data.get('friends')
    description = data.get('description')
    my_spending = data.get('my_spending')
    friends_spending = data.get('friends_spending')

    def updateUser():
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET total_expenses = total_expenses + %s WHERE user_id = %s', (my_spending, user_id))
        mysql.connection.commit()
        cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO bills(user_id, friends, description, my_spending, friends_spending) VALUES(%s, %s, %s, %s, %s)', (user_id, friends, description, my_spending, friends_spending))
    mysql.connection.commit()
    cursor.close()
    updateUser()
    return jsonify({'message': 'Bill added successfully'}), 201

@app.route('/divvyup/addItem', methods=['POST'])
def add_item():
    data = request.get_json()

    user_id = data.get('user_id')
    description = data.get('description')
    item_name = data.get('item_name')
    cost = data.get('cost')
    friends = data.get('friends')

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO items(user_id, description, item_name, cost, friends) VALUES(%s, %s, %s, %s, %s)', (user_id, description, item_name, cost, friends))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Bill added successfully'}), 201

@app.route('/divvyup/getBill', methods=['GET'])
def get_bill():
    try:
        # Get email from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'Email not provided'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM bills WHERE user_id = %s', (user_id,))
        bills = cursor.fetchall()
        description = [""]
        my_spending = [0.0]
        date = [""]
        cursor.close()

        for i in bills:
            if ("Me" in i[2]):
                description.append(i[3])
                my_spending.append(i[4])
                date.append(i[7])

        if bills:
            return jsonify({'description': description, 'my_spending': my_spending, 'date': date}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/addFriend', methods=['POST'])
def add_friend():
    data = request.get_json()

    user_id = data.get('user_id')
    name = data.get('name')

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO friends(user_id, name, expenses) VALUES(%s, %s, 0.0)', (user_id, name))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Friend added successfully'}), 201


if __name__ == "__main__":
    app.run(port=5000, debug=True)
