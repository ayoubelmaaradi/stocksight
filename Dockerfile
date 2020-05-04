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
ADD manage.py ./
#COPY startup.sh ./
RUN python api/service/news_headlines.py &
ENV PYTHONIOENCODING=utf8
#RUN python sentiment.py -s TSLA -k 'Elon Musk',Musk,Tesla,SpaceX --debug &
#RUN python app.py
EXPOSE 3001
ENTRYPOINT ["python", "manage.py", "runserver" ]
