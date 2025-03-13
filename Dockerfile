FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Run as non-root user


RUN  chmod +x entrypoint.sh

USER celeryuser

CMD ["bash", "entrypoint.sh"]
