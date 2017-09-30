FROM python:3.6

WORKDIR /opt/project/feds

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /opt/project/feds/requirements.txt
RUN pip install -r requirements.txt
# Driver needed for Selenium tests.
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz | tar xz -C /usr/local/bin
# Firefox
# Adds add-apt-repository, then installs FF
RUN apt-get update
#RUN apt-get -y dist-upgrade
RUN apt-get install -y firefox-esr
#RUN apt-get install python-software-properties
# Now copy in our code, and run it
COPY . /opt/project/feds
EXPOSE 8000 3306
# RUN service mysql start
CMD python /opt/project/feds/manage.py runserver 0.0.0.0:8000
