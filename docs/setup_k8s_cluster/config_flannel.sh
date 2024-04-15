#!/bin/bash

# Define the file path
FILE_PATH="/run/flannel/subnet.env"

# Content to write to the file
CONTENT="FLANNEL_NETWORK=10.244.0.0/16
FLANNEL_SUBNET=10.244.0.1/24
FLANNEL_MTU=1450
FLANNEL_IPMASQ=true"

# Use echo with a here-document to write the content to the file
# Overwrite the file if it exists
echo "$CONTENT" > $FILE_PATH

echo "The file $FILE_PATH has been created/updated with the specified content."
