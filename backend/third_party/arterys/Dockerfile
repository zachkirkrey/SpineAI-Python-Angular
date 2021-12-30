# This Docker image provides all the components necessary to run SpineAI
# in Arterys mode.

# This is a convenience image that provides CUDA, python3.6, and tensorflow,
# along with some other machine learning convenience libraries (eg. Conda)
FROM tiangolo/python-machine-learning:cuda9.1-python3.6-tensorflow

WORKDIR /app

VOLUME /input
VOLUME /output

# Install python requirements.
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv
COPY Pipfile ./Pipfile
COPY Pipfile.lock ./Pipfile.lock
RUN python3 -m pipenv install

# We copy individual folders to preserve directory structure.
COPY README.md ./README.md
COPY bin ./bin
COPY report ./report
COPY runtime ./runtime
COPY lib ./lib
COPY app.py .

CMD python3 app.py --mode=arterys --src_dir=/input --output_dir=/output
