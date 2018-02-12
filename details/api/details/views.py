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
from sqlalchemy.exc import OperationalError, DataError

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../../')

from lib.database import db_session
from lib.beer.models import Beer
from lib.utils import http_status_response # noqak

logger = logging.getLogger(__name__)
details = Blueprint('details', __name__)

MAX_LIMIT=100

@details.route('', methods=['GET', 'POST'])
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
        except (OperationalError, DataError) as error:
            logger.critical(error)
            abort(500)
        return jsonify(data=beer.to_json, **http_status_response('CREATED')
                      ), HTTPStatus.CREATED.value
    limit = int(request.args.get('limit', 10))
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT
    filter_args = ('name', 'brewery')
    filter_query = str()
    for name in filter_args:
        if request.args.get(name, None):
            filter_name = name
            filter_query = "%%%s%%" % request.args.get(name)
    if filter_query:
        query = Beer.query.filter(getattr(Beer, filter_name).like(filter_query))
    else:
        query = Beer.query
    beers = [beer.to_json for beer in query.order_by(Beer.updated_at.desc()).limit(limit)]
    return jsonify(data=beers, **http_status_response('OK')
                  ), HTTPStatus.OK.value

@details.route('/<int:beer_id>', methods=['GET', 'DELETE'])
def get_or_delete_beer(beer_id):
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
    if request.method == 'DELETE':
        try:
            Beer.query.filter_by(id=beer_id).delete()
            db_session.commit()
            logger.debug("'%s' deleted." % beer_id)
        except (OperationalError, DataError) as error:
            logger.critical(error)
            abort(500)
        return jsonify(**http_status_response('OK')
                      ), HTTPStatus.OK.value
    return jsonify(data=beer.to_json, **http_status_response('OK')
                  ), HTTPStatus.OK.value
