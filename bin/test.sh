#!/bin/bash

set -e


WEB_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_web_1`
PROXY_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_proxy_1`
MQ_IP=`docker inspect --format '{{ .NetworkSettings.Networks.hippo_default.IPAddress }}' hippo_mq_1`


echo "waiting for the mq..."
until (echo > /dev/tcp/$MQ_IP/5672) &>/dev/null
do
	echo "waiting..."
sleep 2
done

echo "waiting for the web..."
until (echo > /dev/tcp/$WEB_IP/8000) &>/dev/null
do
	echo "waiting..."
sleep 2
done

echo "waiting for the proxy..."
until (echo > /dev/tcp/$PROXY_IP/443) &>/dev/null
do
	echo "waiting..."
sleep 2
done


TEMPDIR=`mktemp -d`
TEMPFILE=`mktemp`
INPUT=$TEMPDIR/test.npc
echo "graphs = True" >$INPUT

echo "posting test job..."
JOB_URL=`http -a admin:admin --verify=no --form POST https://$PROXY_IP/jobs/ input@$INPUT public=true | jq -r '.url'`
echo $JOB_URL
[ $JOB_URL == "null" ] && exit 1

echo "retrieving input url..."
INPUT_URL=`http --follow --verify=no $JOB_URL | jq -r '.input'`
echo $INPUT_URL
[ $INPUT_URL == "null" ] && exit 1

echo "checking stored input..."
http --follow --verify=no $INPUT_URL >$TEMPFILE
diff $TEMPFILE $INPUT || exit 1

echo "waiting for job completion..."
JOB_STATE="pending"
while [ $JOB_STATE == "pending" ] || [ $JOB_STATE == "started" ];
do
	echo "waiting for job completion"
	sleep 1
	JOB_STATE=`http --follow --verify=no $JOB_URL | jq -r '.state'`
done
echo $JOB_STATE
[ $JOB_STATE != "finished" ] && exit 1

echo "retrieving output and results urls..."
OUTPUT_URL=`http --follow --verify=no $JOB_URL | jq -r '.output'`
echo $OUTPUT_URL
[ $OUTPUT_URL == "null" ] && exit 1
RESULTS_URL=`http --follow --verify=no $JOB_URL | jq -r '.results'`
echo $RESULTS_URL
[ $RESULTS_URL == "null" ] && exit 1

echo "checking output and results..."
http --headers --follow --verify=no HEAD $OUTPUT_URL | head -n 1 | fgrep "200 OK"
http --headers --follow --verify=no HEAD $RESULTS_URL | head -n 1 | fgrep "200 OK"
