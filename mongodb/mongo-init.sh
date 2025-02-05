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

  db.createUser({
    user: "${MONGO_INITDB_ROOT_USERNAME}",
    pwd: "${MONGO_INITDB_ROOT_PASSWORD}",
    roles: [{ role: 'root', db: 'admin' }]
  });

  // Authenticate as root to create application user
  db.auth("${MONGO_INITDB_ROOT_USERNAME}", "${MONGO_INITDB_ROOT_PASSWORD}");


  use $MONGO_DATABASE
  db.createUser({
    user: "${MONGO_USERNAME}",
    pwd: "${MONGO_PASSWORD}",
    roles: [{ role: 'readWrite', db: "${MONGO_DATABASE}" }]
  });


  db = db.getSiblingDB('$MONGO_DATABASE');
  

 // Create the collection with schema validation
 db.createCollection('$MONGO_COLLECTION_NAME', {
  validator: {
    \$jsonSchema: {
      bsonType: "object",
      required: [
        "student_id",
        "student_userId 
        "student_name", 
        "student_surname", 
        "student_email", 
        "course_id", 
        "course_name",
        "graduation_date",
        "course_description",
        "course_duration",
        "course_level",
        "completionDate"
      ],
      properties: {
        student_id: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        student_userId: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        student_name: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        student_surname: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        student_email: {
          bsonType: "string",
          pattern: "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+\$",
          description: "must be a valid email address"
        },
        course_id: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        course_name: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        course_description: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        course_duration: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        course_level: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        completionDate: {
          bsonType: "string",
          description: "must be of type string in ISO 8601 format"
        },
        blob_link: {
          bsonType: "string",
          description: "URL link to the certificate blob"
        }
      }
    }
  }
});
  

  // Create a unique compound index on student_id and course_id
  db['$MONGO_COLLECTION_NAME'].createIndex(
    { 
      "student_id": 1, 
      "course_id": 1 
    }, 
    { 
      unique: true,
      partialFilterExpression: {
        student_id: { \$type: "string" },
        course_id: { \$type: "string" }
      }
    }
  );

  print('MongoDB initialization completed successfully');
EOF

echo "MongoDB initialization script completed"