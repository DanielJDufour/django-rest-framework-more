#!/bin/sh -e

docker run --name drf-more-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e PG_TRUST_LOCALNET=true postgres