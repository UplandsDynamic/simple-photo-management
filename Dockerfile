FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONIOENCODING=UTF-8
RUN apt update && apt dist-upgrade -y
RUN apt install exiv2 build-essential python-all-dev libexiv2-dev libboost-python-dev libpq-dev locales tzdata netcat curl cmake zlib1g-dev -y
RUN mkdir /repo
RUN mkdir /src
RUN mkdir /config
RUN mkdir /photo_directory
RUN mkdir /var/log/gunicorn
RUN git clone https://github.com/Aninstance/simple-photo-management.git /repo
RUN cp -a /repo/src/. /src
RUN cp -a /repo/config/. /config
RUN rm -rf /repo
RUN pip install -r /config/requirements.txt
RUN curl -LOJ https://github.com/Exiv2/exiv2/archive/v0.27.2.zip
RUN unzip exiv2-0.27.2.zip
RUN rm -rf exiv2-0.27.2.zip
WORKDIR /exiv2-0.27.2
RUN mkdir build
WORKDIR /exiv2-0.27.2/build
RUN cmake .. -DCMAKE_BUILD_TYPE=Release
RUN cmake --build .
#RUN make tests
RUN make install
WORKDIR /src
EXPOSE 8000
VOLUME ["/photo_directory"]
ENTRYPOINT [ "/config/entrypoint-dev-server.sh" ]