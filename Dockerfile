FROM python:3.8-slim-buster

ENV FLASK_APP=currencyexchange
ENV FLASK_DEBUG=1

ENV PROJECT_ROOT /app
WORKDIR $PROJECT_ROOT

# Create a group and user to run our app
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

# create logs dirs
RUN mkdir /var/log/app/ && chmod 777 /var/log/app/

# Copy application
COPY . .
# install python requirements
RUN pip install -q -r requirements.txt

# Apply the migration to the database
RUN flask db upgrade

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

# Start web worker
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app --log-level DEBUG --reload --access-logfile /var/log/app/access.log --error-logfile /var/log/app/error.log
