FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN chmod +x /app/bin/tbox && ln -s /app/bin/tbox /usr/local/bin/tbox
ENTRYPOINT ["tbox"]
