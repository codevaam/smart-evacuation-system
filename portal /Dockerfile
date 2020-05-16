FROM: jjanzic/docker-python3-opencv

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /code
WORKDIR /code
RUN apt --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install numpy
COPY requirements.txt /code/
RUN apt add --no-cache --virtual .build-deps gcc python3-dev\
    && pip install --upgrade pip\
    && pip install --trusted-host pypi.python.org -r requirements.txt \
    && apt del .build-deps