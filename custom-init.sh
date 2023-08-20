#!/bin/bash
set -e

# Start MySQL
/usr/local/bin/docker-entrypoint.sh mysqld &
MYSQL_PID=$!

# Wait for MySQL to become available
until mysql -u root --password="${MYSQL_ROOT_PASSWORD}" -e "SHOW DATABASES;" &> /dev/null; do
    echo "Waiting for MySQL to start"
    sleep 2
done

# Custom initialization
echo "Hello, World!"
mysql -u root --password=${MYSQL_ROOT_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS ${MYSQL_NAME};
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON ${MYSQL_NAME}.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF

# Wait for MySQL to finish
wait $MYSQL_PID
