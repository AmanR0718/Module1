BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="zambian_farmers_backup_${TIMESTAMP}"

echo "📦 Creating backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
docker-compose exec -T mongodb mongodump \
    -u admin \
    -p password123 \
    --authenticationDatabase admin \
    --db zambian_farmers \
    --archive > "${BACKUP_DIR}/${BACKUP_FILE}.archive"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}.archive"

echo "✅ Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.archive.gz"
echo ""
echo "To restore, run:"
echo "  gunzip ${BACKUP_DIR}/${BACKUP_FILE}.archive.gz"
echo "  docker-compose exec -T mongodb mongorestore --archive < ${BACKUP_DIR}/${BACKUP_FILE}.archive"
