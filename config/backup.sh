#!/bin/bash

# A simple script to backup subtenancy data and upload them to Google Drive

GDRIVE=1xXQ_LfwxPMNvJvJowW1EB-KeTudeWOG5
BACKUP=/home/str3/backups/
DBUSER=djangouser
DBNAME=subtenancy
DBHOST=localhost
DATE=$(date +"%Y-%m-%d")
SECONDS=$(date +"%s")

# Create tar containing dump of database and all contract pdf files

mkdir -p ${BACKUP}/backup
tar -cf ${BACKUP}/backup/contracts.tar -C /var/www/ferienmiete/contracts contracts/
pg_dump -h $DBHOST -U $DBUSER -w -F t $DBNAME -f ${BACKUP}/backup/subtenancy.tar
tar -cf ${BACKUP}subtenancy_backup_${DATE}_${SECONDS}.tar -C /home/str3/backups backup/

# Upload backup to gdrive
openssl aes-256-cbc -a -salt -in ${BACKUP}subtenancy_backup_${DATE}_${SECONDS}.tar -out ${BACKUP}subtenancy_backup_${
/home/str3/gdrive/gdrive upload --parent $GDRIVE ${BACKUP}subtenancy_backup_${DATE}_${SECONDS}.tar.enc

# Cleanup files
# find /backups/postgres_backups -name "customerdata*.gz" -mtime +30 -type f -delete
rm -rf /home/str3/backups/backup