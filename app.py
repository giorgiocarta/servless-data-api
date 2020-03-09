from chalice import Chalice
import logging
from chalicelib.some_client import SameClient
from os import environ

app = Chalice(app_name='data-api')

app.log.setLevel(logging.DEBUG)

import boto3

rdsData = boto3.client('rds-data')

cluster_arn = environ.get('AURORA_CLUSTER_ARN')
secret_arn = environ.get('AURORA_SECRET_ARN')
database_name = environ.get('AURORA_DATABASE_NAME')

@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/watchlist')
def watchlist():
    app.log.debug("This is a debug statement")
    app.log.error("This is an error statement")
    myenv = environ.get('TEST','meh')
    a = index()
    return {'hello': 'watchlist', "from_index":  a, "lib": SameClient.execute(), 'myenv': myenv}
