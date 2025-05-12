FROM python:3.11.2


SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim

RUN useradd -rms /bin/bash fb && chmod 777 /opt /run

WORKDIR /fb

RUN mkdir /fb/static && mkdir /fb/media && chown -R fb:fb /fb && chmod 755 /fb

COPY --chown=fb:fb . .

RUN pip install -r requirements.txt

USER fb

CMD ["gunicorn","-b","0.0.0.0:8001"]



