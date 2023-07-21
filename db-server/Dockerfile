FROM python:3.8.10

WORKDIR /neo4j-bloom

COPY ./requirements.txt /neo4j-bloom/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /neo4j-bloom/requirements.txt

COPY . /neo4j-bloom/.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]