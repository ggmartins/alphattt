#!/usr/bin/env bash
#docker scout cves --details my-app:latest
docker scout cves --only-severity critical,high my-app:latest
docker scout recommendations my-app:latest
