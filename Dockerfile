FROM python:3.5

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor net-tools

RUN pip3 install uwsgi

COPY app /app
RUN mkdir /app/log

RUN pip3 install -r /app/requirements.txt

RUN useradd --no-create-home nginx
RUN usermod -a -G nginx www-data

RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache

COPY nginx.conf /etc/nginx/conf.d/
COPY uwsgi_params /etc/nginx/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/

RUN chown -R www-data: /app
WORKDIR /app

CMD ["/usr/bin/supervisord"]