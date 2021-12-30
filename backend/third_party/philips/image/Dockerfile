# This Docker image provides all the components necessary to run SpineAI
# as an Phlips ISD plugin.

# This is a convenience image that provides CUDA, python3.6, and tensorflow,
# along with some other machine learning convenience libraries (eg. Conda)
FROM tensorflow/tensorflow:2.0.1-gpu

WORKDIR /app

VOLUME /input
VOLUME /output

VOLUME /logs

# Install python requirements.
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv
COPY Pipfile ./Pipfile
COPY Pipfile.lock ./Pipfile.lock
RUN python3 -m pipenv install

# We copy individual folders to preserve directory structure.
COPY README.md ./README.md
COPY bin ./bin
COPY report_templates ./report_templates
COPY runtime ./runtime
COPY lib ./lib
COPY third_party/philips ./third_party/philips
COPY app.py .

ENTRYPOINT ["python3", "app.py"]
CMD ["--mode=simple", "--output_type=philips_vsr", "--src_dir=/input", "--output_dir=/output"]
