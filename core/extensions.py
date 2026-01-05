# App Extensions
# Centralizované Flask rozšírenia pre celú aplikáciu

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import redis
import logging

# SQLAlchemy instance
db = SQLAlchemy()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Blueprint route

# Logger
logger = logging.getLogger(__name__)

# Redis client (inicializuje sa v create_app)
redis_client = None


def init_redis(app):
    """Inicializuje Redis klienta z konfigurácie"""
    global redis_client
    try:
        redis_client = redis.StrictRedis.from_url(
            app.config.get('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Redis pripojenie úspešné")
    except Exception as e:
        logger.warning(f"Redis connection warning: {e}")
        redis_client = None
    return redis_client
