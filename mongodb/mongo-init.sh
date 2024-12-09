#!/bin/bash
set -e

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
until mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  sleep 2
done
echo "MongoDB is ready. Starting initialization..."

# Create root user and application user
mongosh admin --quiet <<EOF
  // Create root user first
  db.createUser({
    user: '$MONGO_INITDB_ROOT_USERNAME',
    pwd: '$MONGO_INITDB_ROOT_PASSWORD',
    roles: [{ role: 'root', db: 'admin' }]
  });

  // Authenticate as root to create application user
  db.auth('$MONGO_INITDB_ROOT_USERNAME', '$MONGO_INITDB_ROOT_PASSWORD');

  // Create application user
  use $MONGO_DATABASE
  db.createUser({
    user: '$MONGO_USERNAME',
    pwd: '$MONGO_PASSWORD',
    roles: [{ role: 'readWrite', db: '$MONGO_DATABASE' }]
  });

  // Switch to application database and create collections/indexes
  db = db.getSiblingDB('$MONGO_DATABASE');
  db.createCollection('student_certificates');
  db.certificates.createIndex({ "student_id": 1 });
  db.certificates.createIndex({ "course_id": 1 });
  db.certificates.createIndex({ "certificate_id": 1 }, { unique: true });

  print('MongoDB initialization completed successfully');
EOF

echo "MongoDB initialization script completed"
