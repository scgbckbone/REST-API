from flask_restful import Resource, reqparse
from models.users_alchemy import UserModel
from logging_util import resource_logger as logger


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )
    parser.add_argument(
        'password',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User with this username already exists"}, 400

        user = UserModel(data["username"], data["password"])
        try:
            user.save_to_db()
        except Exception:
            logger.error(
                "Failed to register user: {}".format(user.username),
                exc_info=True
            )

            return {"message": "An error occured saving user"}, 500

        return {"message": "User created successfully"}, 201
