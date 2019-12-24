docker run -d \
--mount type=bind,source=/code/vdca-api/app/data/data_mount,target=/data \
-e API_KEY=$API_KEY \
-e DATABASE_PATH='/data/vdca_db.sqlite' \
-e UPDATE_JOB_LOGFILE_PATH='/data/vdca_update_job_log.txt' \
-e API_LOGFILE_PATH='/data/vdca_api_log.txt' \
-e UPDATE_JOB_CONFIG_PATH='/app/data/update_job_config.yml' \
-p 80:80 \
vdca_api