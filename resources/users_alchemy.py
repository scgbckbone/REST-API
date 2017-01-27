import sqlite3
from flask_restful import Resource, reqparse
from models.users_alchemy import UserModel


class User_register(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
             type=str,
             required=True,
             help="This field cannot be left blank"
    )
    parser.add_argument('password',
             type=str,
             required=True,
             help="This field cannot be left blank"
    )
    def post(self):
        data = User_register.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User with this username already exists"}, 400

        user = UserModel(data["username"], data["password"])  # or insted user = UserModel(**data)
        try:
            user.save_to_db()
        except:
            return {"message": "An error occured saving user"}, 500


        return {"message": "User created successfully"}, 201