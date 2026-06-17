######################################################################
# Copyright 2016, 2026 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Module for Hit Counter Service Routes
"""

from os import getenv
from flask import jsonify, abort, url_for, Response
from flask import current_app as app
from service.common import status  # HTTP Status Codes
from service.models import Counter, DatabaseConnectionError

DEBUG = getenv("DEBUG", "False") == "True"
PORT = getenv("PORT", "8080")


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health() -> tuple[dict, int]:
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


############################################################
# Index page
############################################################
@app.route("/")
def index() -> tuple[Response, int]:
    """Root URL"""
    app.logger.info("Request for Base URL")
    return (
        jsonify(
            status=status.HTTP_200_OK,
            message="Hit Counter Service",
            version="1.0.0",
            url=url_for("list_counters", _external=True),
        ),
        status.HTTP_200_OK,
    )


############################################################
# List counters
############################################################
@app.route("/counters", methods=["GET"])
def list_counters() -> tuple[list[Counter], int]:
    """List counters"""
    app.logger.info("Request to list all counters...")
    counters = []
    try:
        counters = Counter.all()
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return counters, status.HTTP_200_OK


############################################################
# Read counters
############################################################
@app.route("/counters/<name>", methods=["GET"])
def read_counters(name: str) -> tuple[dict, int]:
    """Read a counter"""
    app.logger.info("Request to Read counter: %s...", name)

    try:
        counter = Counter.find(name)
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    if not counter:
        abort(status.HTTP_404_NOT_FOUND, f"Counter {name} does not exist")

    app.logger.info("Returning: %d...", counter.value)
    return counter.serialize(), status.HTTP_200_OK


############################################################
# Create counter
############################################################
@app.route("/counters/<name>", methods=["POST"])
def create_counters(name: str) -> tuple[dict, int, dict]:
    """Create a counter"""
    app.logger.info("Request to Create counter...")
    try:
        counter = Counter.find(name)
        if counter is not None:
            abort(status.HTTP_409_CONFLICT, f"Counter '{name}' already exists")

        counter = Counter(name)
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    location_url = url_for("read_counters", name=name, _external=True)
    return (
        counter.serialize(),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


############################################################
# Update counters
############################################################
@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name: str) -> tuple[Response, int]:
    """Update a counter"""
    app.logger.info("Request to Update counter...")
    try:
        counter = Counter.find(name)
        if counter is None:
            return jsonify(code=404, error=f"Counter {name} does not exist"), 404

        count = counter.increment()
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return jsonify(name=name, counter=count), status.HTTP_200_OK


############################################################
# Delete counters
############################################################
@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name: str) -> tuple[dict, int]:
    """Delete a counter"""
    app.logger.info("Request to Delete counter...")
    try:
        counter = Counter.find(name)
        if counter:
            del counter.value
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return {}, status.HTTP_204_NO_CONTENT
