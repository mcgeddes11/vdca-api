docker run -d \
--mount type=bind,source=/home/joncocks/data,target=/data \
-e API_KEY=$API_KEY \
-e DATABASE_PATH='/data/vdca_db.sqlite' \
-e UPDATE_JOB_LOGFILE_PATH='/data/vdca_update_job_log.txt' \
-e API_LOGFILE_PATH='/data/vdca_api_log.txt' \
-p 80:80 \
vdca_api