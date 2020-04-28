FROM python:alpine

RUN pip install pyyaml paho-mqtt

COPY ./script-runner.py /src/script-runner.py
WORKDIR /src

CMD ["python","-u","script-runner.py","-c","/src/mqtt/scripts.yaml"]
