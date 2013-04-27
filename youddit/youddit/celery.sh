if [[ "$1" == "start" ]]; then  
    echo "starting"
    celery worker -A workers -c 5 -l debug > celery.log 2> celery.log &
elif [[ "$1" == "stop" ]]; then  
    echo "stoping"
    ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
fi
