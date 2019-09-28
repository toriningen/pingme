FROM node:12.10.0-alpine

COPY app /app
WORKDIR /app
RUN npm i

ENV API_TOKEN=""
ENV CHAT_ID=""
ENV PORT="8080"

CMD ["node", "/app/index.js"]
