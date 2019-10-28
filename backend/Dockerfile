FROM alpine:latest as build-stage

RUN apk update && apk add make cmake gcc g++ git libgcc openssl-dev sqlite-dev

COPY app app

WORKDIR /app/src

RUN cmake . && make -o ../app

EXPOSE 6969