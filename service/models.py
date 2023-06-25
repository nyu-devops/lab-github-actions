######################################################################
# Copyright 2016, 2023 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Counter Model
"""
import logging
from redis.exceptions import ConnectionError as RedisConnectionError
from service import redis

logger = logging.getLogger(__name__)


class DatabaseConnectionError(RedisConnectionError):
    """Generic Exception for Redis database connection errors"""


class Counter:
    """An integer counter that is persisted in Redis

    You can establish a connection to Redis using an environment
    variable DATABASE_URI in the following format:

        DATABASE_URI="redis://userid:password@localhost:6379/0"

    This follows the same standards as SQLAlchemy URIs
    """

    def __init__(self, name: str = "hits", value: int = None):
        """Constructor"""
        self.name = name
        if not value:
            self.value = 0
        else:
            self.value = value

    @property
    def value(self):
        """Returns the current value of the counter"""
        return int(redis.get(self.name))

    @value.setter
    def value(self, value):
        """Sets the value of the counter"""
        redis.set(self.name, value)

    @value.deleter
    def value(self):
        """Removes the counter fom the database"""
        redis.delete(self.name)

    def increment(self):
        """Increments the current value of the counter by 1"""
        return redis.incr(self.name)

    def serialize(self):
        """Converts a counter into a dictionary"""
        return {
            "name": self.name,
            "counter": int(redis.get(self.name))
        }

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################

    @classmethod
    def all(cls):
        """Returns all of the counters"""
        try:
            counters = [
                {"name": key, "counter": int(redis.get(key))}
                for key in redis.keys("*")
            ]
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return counters

    @classmethod
    def find(cls, name):
        """Finds a counter with the name or returns None"""
        counter = None
        try:
            count = redis.get(name)
            if count:
                counter = Counter(name, count)
        except Exception as err:
            raise DatabaseConnectionError(err) from err
        return counter

    @classmethod
    def remove_all(cls):
        """Removes all of the keys in the database"""
        try:
            redis.flushall()
        except Exception as err:
            raise DatabaseConnectionError(err) from err
