FROM python:3.10.16-slim-bookworm

SHELL ["/bin/bash", "-c"]

ENV APP_DIR="/app"
ENV VENV_DIR="/venv"

RUN mkdir -p "${APP_DIR}" \
    && mkdir -p "${VENV_DIR}"

COPY ./fiap_datathon_app ${APP_DIR}/fiap_datathon_app
COPY ./sh ${APP_DIR}/sh

RUN python -m venv "${VENV_DIR}" \
    && source ${VENV_DIR}/bin/activate \
    && ${APP_DIR}/sh/00-install-api.sh

ENTRYPOINT source ${VENV_DIR}/bin/activate \
    && uvicorn fiap_datathon_app.api:app --reload --host 0.0.0.0 --port 8000

    