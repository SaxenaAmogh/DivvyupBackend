from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    total_expenses = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Friend(db.Model):
    __tablename__ = 'friends'
    friend_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    expenses = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    __tablename__ = 'bills'
    bill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    friends = db.Column(db.String(255))
    description = db.Column(db.String(255))
    my_spending = db.Column(db.Float)
    friends_spending = db.Column(db.Float)
    total_spending = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    description = db.Column(db.String(255))
    item_name = db.Column(db.String(255))
    cost = db.Column(db.Float)
    friends = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'
    expense_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    description = db.Column(db.String(255))
    items= db.Column(db.String(255))
    cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

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

        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/users', methods=['GET'])
def get_users():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'message': 'Email not provided'}), 400

        user = User.query.filter_by(email=email).first()

        if user:
            return jsonify(user.user_id), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/profile', methods=['GET'])
def get_profile():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'User ID not provided'}), 400

        user = User.query.get(user_id)

        if user:
            return jsonify({'username': user.username, 'email': user.email, 'expense': user.total_expenses}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/expense', methods=['GET'])
def get_expense():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'User ID not provided'}), 400

        user = User.query.get(user_id)

        if user:
            return jsonify(user.total_expenses), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/friends', methods=['GET'])
def get_friends():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'User ID not provided'}), 400

        friends = Friend.query.filter_by(user_id=user_id).all()
        friend_names = " ".join([friend.name for friend in friends])
        friend_num = len(friends)

        if friends:
            return jsonify({'friends': friend_names, 'friend_num': friend_num}), 200
        else:
            return jsonify({'message': 'No friends found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/addBill', methods=['POST'])
def add_bill():
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        friends = data.get('friends')
        description = data.get('description')
        my_spending = data.get('my_spending')
        friends_spending = data.get('friends_spending')

        new_bill = Bill(user_id=user_id, friends=friends, description=description,
                        my_spending=my_spending, friends_spending=friends_spending, total_spending=my_spending + friends_spending)
        db.session.add(new_bill)

        user = User.query.get(user_id)
        user.total_expenses += my_spending

        db.session.commit()
        return jsonify({'message': 'Bill added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/addItem', methods=['POST'])
def add_item():
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        description = data.get('description')
        item_name = data.get('item_name')
        cost = data.get('cost')
        friends = data.get('friends')

        new_item = Item(user_id=user_id, description=description, item_name=item_name,
                        cost=cost, friends=friends)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/getBill', methods=['GET'])
def get_bill():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'User ID not provided'}), 400

        bills = Bill.query.filter_by(user_id=user_id).all()
        description = [""]
        my_spending = [0.0]
        date = [""]

        for bill in bills:
            if "Me" in bill.friends:
                description.append(bill.description)
                my_spending.append(bill.my_spending)
                date.append(bill.created_at.strftime("%Y-%m-%d %H:%M:%S"))

        if bills:
            return jsonify({'description': description, 'my_spending': my_spending, 'date': date}), 200
        else:
            return jsonify({'message': 'No bills found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/divvyup/addFriend', methods=['POST'])
def add_friend():
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        name = data.get('name')

        new_friend = Friend(user_id=user_id, name=name)
        db.session.add(new_friend)
        db.session.commit()
        return jsonify({'message': 'Friend added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
