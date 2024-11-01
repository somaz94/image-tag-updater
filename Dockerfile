# Use a lightweight base image
FROM alpine:3.20

# Install necessary packages
RUN apk add --no-cache \
    git=2.45.2-r0 \
    bash=5.2.26-r0 \
    gawk=5.3.0-r1 \
    sed=4.9-r2 

# Set the working directory inside the container    
WORKDIR /usr/src

# Copy any source file(s) required for the action
COPY entrypoint.sh .

# Configure the container to be run as an executable
ENTRYPOINT ["/usr/src/entrypoint.sh"]