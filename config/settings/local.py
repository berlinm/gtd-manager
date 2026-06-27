from .base import *  # noqa: F401, F403

# Development-only secret key. Replace with a strong random value before
# any production deployment. See docs/SECURITY.md.
SECRET_KEY = 'dev-only-insecure-key-do-not-use-in-production-change-before-deploy'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
