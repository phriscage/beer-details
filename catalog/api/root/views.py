# pylint: disable=broad-except,invalid-name,import-error,wrong-import-position
"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
# from datetime import datetime
from http import HTTPStatus
import logging
# from urllib.parse import urlparse, unquote
from flask import Blueprint, jsonify, request, abort
from sqlalchemy.exc import OperationalError

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../../')

from lib.database import db_session
from lib.beer.models import Beer
from lib.utils import http_status_response, get_fqdn, get_ip_address # noqa

logger = logging.getLogger(__name__)
root = Blueprint('main', __name__)


def sample_response(extra_data=None):
    """ sample response that is used for all resources """
    # logger.debug(request.headers.environ)
    data = {
        'host': {
            'fqdn': get_fqdn(),
            'ip_address': get_ip_address()
        },
        'extra_data': extra_data,
        'request': {
            'url': request.url
        }
    }
    return jsonify(data=data, **http_status_response('OK')
                  ), HTTPStatus.OK.value

@root.route('/test', methods=['GET'])
def test():
    """
    **Example request:**

    .. sourcecode:: http

    GET HTTP/1.1
    Accept: */*

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: Ok
    :statuscode 500: server error
    """
    return sample_response()

@root.route('/health', methods=['GET'])
def health():
    """
    **Example request:**

    .. sourcecode:: http

    GET HTTP/1.1
    Accept: */*

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: Ok
    :statuscode 500: server error
    """
    try:
        db_session.execute('SELECT 1 as is_alive;')
    except Exception as error:
        logger.critical(error)
        abort(500)
    return jsonify(message="All is well!", **http_status_response('OK')
                  ), HTTPStatus.OK.value

@root.route('/', methods=['GET', 'POST'])
def index():
    """
    **Example request:**

    .. sourcecode:: http

    GET HTTP/1.1
    Accept: */*

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: Ok
    :statuscode 500: server error
    """
    if request.method == 'POST':
        try:
            beer = Beer(**request.json)
        except TypeError as error:
            logger.warning(error)
            abort(400)
        try:
            db_session.add(beer)
            db_session.commit()
            logger.debug(beer)
        except OperationalError as error:
            logger.critical(error)
            abort(500)
        return jsonify(data=beer.to_json, **http_status_response('CREATED')
                      ), HTTPStatus.CREATED.value
    limit = request.args.get('limit', 10)
    beers = [beer.to_json for beer in Beer.query.order_by(Beer.updated_at.desc()).limit(limit)]
    return jsonify(data=beers, **http_status_response('OK')
                  ), HTTPStatus.OK.value

@root.route('/<int:beer_id>', methods=['GET'])
def get_catalog(beer_id):
    """
    **Example request:**

    .. sourcecode:: http

    GET HTTP/1.1
    Accept: */*

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: Ok
    :statuscode 500: server error
    """
    try:
        beer = Beer.query.filter_by(id=beer_id).first()
    except OperationalError as error:
        logger.critical(error)
        abort(500)
    if not beer:
        abort(404)
    return jsonify(data=beer.to_json, **http_status_response('OK')
                  ), HTTPStatus.OK.value
