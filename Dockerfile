FROM gorialis/discord.py:3.12.2-alpine-pypi-minimal
RUN python -m pip install redis
RUN python -m pip install -U discord.py

WORKDIR /usr/src/app
COPY src/ ./
COPY token.txt .

CMD ["python", "./main.py"]

