# pylint: disable=broad-except,invalid-name,import-error,wrong-import-position
"""
    This sample client will simulate a mobile device registration flow for
    PasswordGrant and PasswordGrant with OTP
"""
import os
import sys
import argparse
import logging
from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../')

from lib.database import db_session
#from lib.utils import http_status_response, PythonObjectEncoder # noqa
from lib.utils import PythonObjectEncoder # noqa

APP_SECRET_KEY = os.urandom(32)

logger = logging.getLogger(__name__)


def create_app():
    """ dynamically create the app """
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    #init_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_recycle=3600)
    app.secret_key = APP_SECRET_KEY
    app.json_encoder = PythonObjectEncoder

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """ remove db_session """
        db_session.remove()

    #@app.before_request
    #def before_request():
        #""" create the db_session global if it does not exist """
        #if not hasattr(g, 'db_session'):
            #g.db_session = db_session
        #if not hasattr(g, 'queue_client'):
            #g.queue_client = connect_queue()

    def default_error_handle(error=None):
        """ create a default json error handle """
        return jsonify(message=error.name, description=error.description,
                       success=False), error.code

    # handle all errors with json output
    for error in list(range(400, 420)) + list(range(500, 506)):
        if error not in [402, 407, 419]:  # not all are keys in app.errorhandler
            app.errorhandler(error)(default_error_handle)

    # add each api Blueprint and create the base route
    #from root.views import root
    #app.register_blueprint(root, url_prefix="")
    from health.views import health
    app.register_blueprint(health, url_prefix="/health")
    from details.views import details
    app.register_blueprint(details, url_prefix="/details")
    return app


def bootstrap(**kwargs):
    """bootstraps the application. can handle setup here"""
    app = create_app()
    app.debug = True
    app.run(host=kwargs['host'], port=kwargs['port'], threaded=True)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=("%(asctime)s %(levelname)s %(name)s[%(process)s] : %(funcName)s"
                " : %(message)s"),
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname or IP address", dest="host",
                        type=str, default='0.0.0.0')
    parser.add_argument("--port", help="Port number", dest="port", type=int,
                        default=8080)
    args = parser.parse_args()
    bootstrap(**args.__dict__)
