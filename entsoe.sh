#!/bin/bash

# Set the timestamp for all logs
timestamp=$(date +'%Y%m%d_%H%M')

# Function to log responses to a timestamped file
log_response() {
    response_file="/home/ubuntu/jobs/response_$timestamp.txt"
    echo "Response for $1" >> "$response_file"
    echo "---------------------" >> "$response_file"
    cat - >> "$response_file"
    echo "" >> "$response_file"
}

# Path to the cookies file
COOKIES_FILE="cookies.txt"

# API URLs
SIGN_IN_URL="http://localhost:3000/api/auth/sign-in"
ENTSOE_URL="http://localhost:3000/api/entsoe-sync/sync"
SIGN_OUT_URL="http://localhost:3000/api/auth/sign-out"

# cURL command to sign in and save cookies
curl -d '{"email":"simon.callan78@outlook.com","password":"I5DD0PhOSnwJwJk"}' -H 'Content-Type: application/json' -c "$COOKIES_FILE" "$SIGN_IN_URL" | log_response "Sign In"

# cURL command to access the group endpoint using saved cookies
curl -X POST -b "$COOKIES_FILE" -H 'Content-Type: application/json' "$ENTSOE_URL" | log_response "Entsoe sync"

# cURL command to sign out and update cookies
curl -X DELETE -b "$COOKIES_FILE" -H 'Content-Type: application/json' -c "$COOKIES_FILE" "$SIGN_OUT_URL" | log_response "Sign Out"
