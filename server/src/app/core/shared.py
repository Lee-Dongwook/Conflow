import logging

# init logger using uvicorn.error
logger = logging.getLogger('uvicorn.error')

# global shared variables
scheduler = None
celery_enabled = False

