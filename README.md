[![CI](https://github.com/aiven-recruitment/Python-20221220-vromanuk/actions/workflows/ci.yml/badge.svg)](https://github.com/aiven-recruitment/Python-20221220-vromanuk/actions/workflows/ci.yml)

## Assignment
Your task is to implement a system that monitors website availability over the network, 
produces metrics about this and passes these events 
through an `Aiven Kafka` instance into an `Aiven PostgreSQL` database.

## Service Architecture

![bLFHRjDG37tFLrX5GfiG4apY9L8HR1fze8X09_62X9nSDx6Q-1RxfcHyFRTfbvMG3IqFUR1zpl4vrdrd0JMqJPtOXcMBYWqO_Mn92dglwd_TL5niXCpWucH4VIkky2gayEQatc3Na1cMPFoRuFN5gmdUB2fomLkK0966j6QXf697iFO-vBux0LtwBaFdMCguG9B49io-KGuh3cGpUFPPKKfA87w5hsig0dinQBMsXCH111nH](https://user-images.githubusercontent.com/16399270/209328680-4fad8049-d0dd-4d09-8bf6-d7602e7cceb2.png)


## Installation 👾

Install Pipenv and Dependencies:

```shell
$ make install
```

## Configuration and launch 🚀

1. Specify connection details to `Kafka` and `Postgres` in `.env-local`

2. Download SSL certificates and set proper names for files in `.env-local`.

3. Launch consumer & producer:
```shell
$ make consumer
$ make producer
```
