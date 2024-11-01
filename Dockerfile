# Use a lightweight base image
FROM alpine:3.20

# Install necessary packages
RUN apk add --no-cache \
    git=2.45.2-r0 \
    bash=5.2.26-r0 \
    gawk=5.3.0-r1 \
    sed=4.9-r2 

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the default entrypoint
ENTRYPOINT ["/entrypoint.sh"]