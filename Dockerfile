FROM python:3.6.5-alpine3.7
MAINTAINER techology@unleashed.be

ENV UID=1000 \
  GUID=1000 \
  SHELL=/bin/sh
ARG USER=sms
ARG ROOT=/app

WORKDIR ${ROOT}

RUN addgroup -S -g ${GUID} ${USER} \
  && adduser -S -g ${USER} -u ${UID} ${USER}

RUN pip install -U pip==10.0.1

COPY requirements/requirements.txt /tmp/requirements.txt
RUN pip install --no-deps -r /tmp/requirements.txt

COPY requirements/requirements_test.txt /tmp/requirements_test.txt
RUN pip install --no-deps -r /tmp/requirements_test.txt

RUN chown ${USER}:${USER} -R .

USER ${USER}
