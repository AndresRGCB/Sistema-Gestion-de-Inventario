#!/bin/bash

DB_NAME="inventory_db"  
DB_USER="inventory_user"  
BACKUP_DIR="./backups"
TIMESTAMP=$(date +'%Y-%m-%d_%H-%M-%S')
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"


pg_dump -U $DB_USER -d $DB_NAME -F c -f "$BACKUP_FILE"

ls -t ${BACKUP_DIR}/backup_*.sql | tail -n +6 | xargs rm -f

echo "Backup saved at: $BACKUP_FILE"
