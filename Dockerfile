# Use a lightweight base image
FROM alpine:3.14

# Install necessary packages
RUN apk add --no-cache bash git

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the default entrypoint
ENTRYPOINT ["/entrypoint.sh"]