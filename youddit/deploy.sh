NUM_WORKERS=3
LOGFILE=/var/log/gunicorn/youddit.log
LOGDIR=$(dirname $LOGFILE)

sudo test -d $LOGDIR || mkdir $LOGDIR
sudo gunicorn_django -b 0.0.0.0:3000 -w $NUM_WORKERS --log-level=debug --log-file=$LOGFILE &2>>$LOGFILE 
