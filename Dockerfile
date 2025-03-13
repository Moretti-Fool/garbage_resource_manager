FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .



RUN  chmod +x entrypoint.sh
# Run as non-root user
# USER celeryuser

CMD ["bash", "entrypoint.sh"]
