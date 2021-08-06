FROM python:3.8-slim

# Copy the connector
COPY src /opt/opencti-connector-sftp-receiver

# Install Python modules
RUN apt-get update -y && \
    apt-get install -y git libmagic1 && \
    cd /opt/opencti-connector-sftp-receiver && \
    pip3 install --no-cache-dir -r requirements.txt

# required for updating site-packages
ENV PYTHONPATH="/usr/lib/python3.8/site-packages"

# Expose and entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
