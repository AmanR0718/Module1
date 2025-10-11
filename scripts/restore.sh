if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    echo "Example: ./restore.sh backups/zambian_farmers_backup_20250101_120000.archive.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  This will replace the current database!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Extract if gzipped
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Extracting backup..."
    gunzip -k "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

echo "Restoring database..."
docker-compose exec -T mongodb mongorestore \
    -u admin \
    -p password123 \
    --authenticationDatabase admin \
    --drop \
    --archive < "$BACKUP_FILE"

echo "✅ Database restored successfully!"
