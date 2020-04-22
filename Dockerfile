FROM python:3.6

LABEL maintainer="shirosai"

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
RUN python -m pip install "urllib3<1.25"
COPY sentiment.py ./
COPY stockprice.py ./
ADD api ./
COPY startup.sh ./

ENV PYTHONIOENCODING=utf8
#RUN python sentiment.py -s TSLA -k 'Elon Musk',Musk,Tesla,SpaceX --debug &
#RUN python app.py
EXPOSE 8080
ENTRYPOINT [ "bash", "startup.sh" ]
