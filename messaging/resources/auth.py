# -*- coding: utf-8 -*-


from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from toolz import merge

from messaging.models.user import User as UserModel
from messaging import helpers
from messaging.utils import pick
from messaging.exceptions import InvalidCredential


def sign_up():
    data = request.get_json()
    fields = merge(
        pick(["email", "name"], data),
        {
            "password_hash": generate_password_hash(
                data.get("password"), method="sha256"
            )
        },
    )
    user = helpers.make_create(UserModel, ["email", "name", "password_hash"], "email")(
        fields, as_obj=True
    )
    access_token = create_access_token(identity=user.key.urlsafe())
    return jsonify({"access_token": access_token})


def login():
    data = request.get_json()
    user = UserModel.get_by_id(data.get("email"))
    if not user or not check_password_hash(user.password_hash, data.get("password")):
        raise InvalidCredential()
    access_token = create_access_token(identity=user.key.urlsafe())
    return jsonify({"access_token": access_token})
