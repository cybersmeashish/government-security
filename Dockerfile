FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/lab-state
COPY requirements.lock /dependencies/requirements.lock
COPY vendor/wheels /dependencies/wheels
RUN python -m pip install --no-index --no-cache-dir --require-hashes --find-links=/dependencies/wheels -r /dependencies/requirements.lock
WORKDIR /government
COPY govlab govlab
COPY tools tools
COPY tests tests
COPY examples examples
COPY references references
COPY requirements.lock Dockerfile ./
COPY vendor/reference /reference
USER 65532:65532
CMD ["python", "-m", "tools.exercise", "--reference-root", "/reference", "--require-isolation"]
