FROM python:3.6

WORKDIR /opt/project/feds

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /opt/project/feds/requirements.txt
RUN pip install -r requirements.txt

# Now copy in our code, and run it
COPY . /opt/project/feds
EXPOSE 8000
CMD python /opt/project/feds/feds/feds/manage.py runserver 0.0.0.0:8000
