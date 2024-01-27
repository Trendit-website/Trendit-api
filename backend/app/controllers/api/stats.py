import logging
from flask import request
from flask_jwt_extended import get_jwt_identity

from config import Config
from ...models.task import Task, AdvertTask, EngagementTask
from ...models.user import Trendit3User


class StatsController():
    @staticmethod
    def get_stats():
        pass