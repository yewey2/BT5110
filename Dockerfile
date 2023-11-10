FROM python:3.9.16-slim

RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY . .

RUN pip install -r requirements.txt

# CMD gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app;
CMD [ "guincorn", "-k" , "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "run:app"]