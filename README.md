# OpenCTI-Connector SFTP
OpenCTI connector that parses JSON/STIX files from an SFTP server.

## Usage with the OpenCTI Platform (Docker)
1. Clone repo  
`git clone https://github.com/timebotdon/opencti-connector-sftp-receiver`

2. cd into repo:  
   `cd opencti-connector-sftp-receiver`

3. Copy/paste the following lines:  
   from `opencti-connector-sftp-receiver/docker-compose.yml`  
   to your OpenCTI docker deployment `/path/to/docker-compose.yml`
  ```
  connector-sftp-receiver:
    image: opencti/connector-sftp-receiver:rolling
    environment:
      - OPENCTI_URL=http://opencti:8080
      - OPENCTI_TOKEN=ChangeMe
      - CONNECTOR_ID=ChangeMe
      - CONNECTOR_TYPE=EXTERNAL_IMPORT
      - CONNECTOR_NAME=SFTP Receiver
      - CONNECTOR_SCOPE=ChangeMe
      - CONNECTOR_CONFIDENCE_LEVEL=3
      - CONNECTOR_UPDATE_EXISTING_DATA=False
      - CONNECTOR_LOG_LEVEL=info
      - SFTP_SERVER_ADDRESS=192.168.2.129
      - SFTP_USERNAME=opencti
      - SFTP_PASSWORD=P@55w0rd
      - SFTP_FOLDER_IN=in
      - SFTP_INTERVAL=600 # Seconds (10 minutes)
    restart: always
  ```
4. **Important!** Ensure to update any `ChangeMe` strings in your OpenCTI docker
   deployment.

5. Build the connector:  
   `docker build -t opencti/connector-sftp-receiver:rolling .`

6. Update/Run:  
   `docker-compose -f opencti-docker-compose-file.yml up -d` from OpenCTI docker.


For more information on deploying a custom connector, visit [here](https://www.notion.so/HowTo-Build-your-first-connector-06b2690697404b5ebc6e3556a1385940)
