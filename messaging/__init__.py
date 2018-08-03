from flask import Flask

app = Flask(__name__)


import messaging.views  # NOQA
assert messaging.views
