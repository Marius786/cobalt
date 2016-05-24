from flask import Flask, request
from flask_restful import Api as RestApi


errors = {
    'EtcdConnectionFailed': {
        'message': "The ETCD cluster is not responding.",
        'status': 503,
    }
}

config = {
    'RESTFUL_JSON': {
        'separators': (', ', ': '),
        'indent': 2,
        'sort_keys': False
    }
}


app = Flask(__name__)
app.config.update(**config)


# TODO Disable this for error handling to take effect
app.debug = True

api = RestApi(app, errors=errors, catch_all_404s=True)
