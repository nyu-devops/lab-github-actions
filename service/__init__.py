# Copyright 2016, 2020 John J. Rofrano. All Rights Reserved.
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

"""
Package for the application models and service routes
"""
import os
from flask import Flask
from service.common import log_handlers

# NOTE: Do not change the order of this code
# The Flask app must be created
# BEFORE you import modules that depend on it !!!

DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")

# Create the Flask aoo
app = Flask(__name__)

# Import the routes After the Flask app is created
# pylint: disable=wrong-import-position, wrong-import-order, cyclic-import
from service import routes, models  # noqa: F401, E402
from service.common import error_handlers  # noqa: F401, E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  H I T   C O U N T E R   S E R V I C E  ".center(70, "*"))
app.logger.info(70 * "*")

app.logger.info("Service initialized!")
