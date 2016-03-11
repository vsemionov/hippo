#!/bin/bash

set -e


WEB_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_web_1`
PROXY_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_proxy_1`
MQ_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_mq_1`


echo "waiting for the web service..."
until (echo > /dev/tcp/$WEB_IP/8000) &>/dev/null
do
	echo "waiting..."
sleep 2
done

echo "waiting for the proxy service..."
until (echo > /dev/tcp/$PROXY_IP/443) &>/dev/null
do
	echo "waiting..."
sleep 2
done

echo "waiting for the mq service..."
until (echo > /dev/tcp/$MQ_IP/5672) &>/dev/null
do
	echo "waiting..."
sleep 2
done


TEMPDIR=`mktemp -d`
echo "graphs = True" >$TEMPDIR/test.npc

echo "posting test job..."
JOB_URL=`http -a admin:admin --verify=no --form POST https://$PROXY_IP/jobs/ input@$TEMPDIR/test.npc public=true | jq -r '.url'`
[ $JOB_URL == "null" ] && exit 1

echo "waiting for output and results..."
http --headers --follow --verify=no HEAD $JOB_URL | head -n 1 | fgrep "200 OK"
OUTPUT_URL=null
while [ $OUTPUT_URL == "null" ]; do echo "waiting for output..."; sleep 1; OUTPUT_URL=`http --follow --verify=no $JOB_URL | jq -r '.output'`; done
RESULTS_URL=null
while [ $RESULTS_URL == "null" ]; do echo "waiting for results..."; sleep 1; RESULTS_URL=`http --follow --verify=no $JOB_URL | jq -r '.output'`; done

echo "checking output and results..."
http --headers --follow --verify=no HEAD $OUTPUT_URL | head -n 1 | fgrep "200 OK"
http --headers --follow --verify=no HEAD $RESULTS_URL | head -n 1 | fgrep "200 OK"
