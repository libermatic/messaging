# -*- coding: utf-8 -*-


from werkzeug.security import check_password_hash
from flask import request, jsonify
from flask_jwt_extended import create_access_token

from messaging.models.user import User as UserModel
from messaging.exceptions import InvalidCredential


def login():
    data = request.get_json()
    user = UserModel.get_by_id(data.get("email"))
    if not user or not check_password_hash(user.password_hash, data.get("password")):
        raise InvalidCredential()
    access_token = create_access_token(identity=user.key.urlsafe())
    return jsonify({"access_token": access_token})
