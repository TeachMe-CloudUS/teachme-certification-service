#!/bin/bash
set -e

# URL decode the password
urldecode() {
    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

# Get the decoded password
DECODED_PASSWORD=$(urldecode "$MONGO_INITDB_ROOT_PASSWORD")

mongosh <<EOF
use admin
db.createUser({
  user: '$MONGO_INITDB_ROOT_USERNAME',
  pwd: '$DECODED_PASSWORD',
  roles: [
    { role: 'root', db: 'admin' },
    { role: 'dbOwner', db: '$MONGO_INITDB_DATABASE' }
  ]
})
EOF
