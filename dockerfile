FROM python:3.10

ADD . .

ENV PYTHONPATH "${PYTHONPATH}:/"

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/docker_entrypoint.sh"]