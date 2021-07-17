# API version 4.5.4
# OpenCTI version 4.5.4

import os
from typing import Optional, Dict, Any, Mapping
import yaml
import time
from re import search
from base64 import b64decode
import datetime
import pysftp
from pycti import OpenCTIConnectorHelper, get_config_variable


class SftpReceiver:

    _STATE_LAST_RUN = "last_run"

    def __init__(self):
        # Instantiate the connector helper from config
        config_file_path = os.path.dirname(
            os.path.abspath(__file__)) + "/config.yml"
        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )
        self.helper = OpenCTIConnectorHelper(config)
        # Extra config
        self.sftp_server_address = get_config_variable(
            "SFTP_SERVER_ADDRESS",
            ["sftp-receiver", "server_address"],
            config,
            False,
        )
        self.sftp_username = get_config_variable(
            "SFTP_USERNAME",
            ["sftp-receiver", "username"],
            config,
            False,
        )
        self.sftp_password = get_config_variable(
            "SFTP_PASSWORD",
            ["sftp-receiver", "password"],
            config,
            False,
        )
        self.sftp_folder_in = get_config_variable(
            "SFTP_FOLDER_IN",
            ["sftp-receiver", "folder_in"],
            config,
            False,
        )
        self.sftp_interval = get_config_variable(
            "SFTP_INTERVAL",
            ["sftp-receiver", "interval"],
            config,
            True,
        )
        self.update_existing_data = get_config_variable(
            "CONNECTOR_UPDATE_EXISTING_DATA",
            ["connector", "update_existing_data"],
            config,
            False
        )

        self.temp_dir = 'temp'
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def get_interval(self) -> int:
        return int(self.sftp_interval)

    def fetch_sftp(self):
        try:

            # sftp connection options - disable host key verification
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(host=self.sftp_server_address, username=self.sftp_server_address, password=self.sftp_password, cnopts=cnopts) as sftp:
                try:
                    self.helper.log_info("SSH Connection established. Copying contents of directory..")
                    sftp.get_r(self.sftp_folder_in, self.temp_dir)
                    self.helper.log_info("Contents copied!")
                except Exception as e:
                    self.helper.log_error(str(e))

            # for each file in temp folder, ingest the file, then remove json.
            if os.listdir(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    self.helper.log_info("Pushing " + file + " to OpenCTI..")
                    filePath = self.temp_dir + '/' + file
                    with open(filePath, "r") as data:
                        self.helper.log_info("Pushing to OpenCTI..")
                        self.helper.send_stix2_bundle(bundle=data.read(), update=self.update_existing_data)
                        os.remove(filePath)

            self.helper.log_info("Temp files cleared.")

        except Exception as ex:
            self.helper.log_error(str(ex))
            self.helper.log_info("Error detected. Purging Temp files.")
            # Remove old temp files
            for file in os.listdir(self.temp_dir):
                filePath = self.temp_dir + '/' + file
                os.remove(filePath)

    def _load_state(self) -> Dict[str, Any]:
        current_state = self.helper.get_state()
        if not current_state:
            return {}
        return current_state

    def _is_scheduled(self, last_run: Optional[int], current_time: int) -> bool:
        if last_run is None:
            return True
        time_diff = current_time - last_run
        return time_diff >= self.get_interval()

    @staticmethod
    def _get_state_value(
        state: Optional[Mapping[str, Any]], key: str, default: Optional[Any] = None
    ) -> Any:
        if state is not None:
            return state.get(key, default)
        return default

    @staticmethod
    def _current_unix_timestamp() -> int:
        return int(time.time())

    def run(self):
        self.helper.log_info("Fetching Stix data...")
        while True:
            try:

                timestamp = self._current_unix_timestamp()
                current_state = self._load_state()

                self.helper.log_info(f"Loaded state: {current_state}")

                last_run = self._get_state_value(
                    current_state, self._STATE_LAST_RUN)
                if self._is_scheduled(last_run, timestamp):

                    # fetch data and send as stix bundle
                    self.fetch_sftp()

                    new_state = current_state.copy()
                    new_state[self._STATE_LAST_RUN] = self._current_unix_timestamp()

                    self.helper.log_info(f"Storing new state: {new_state}")

                    self.helper.set_state(new_state)

                    self.helper.log_info(
                        f"State stored, next run in: {self.get_interval()} seconds"
                    )
                else:
                    new_interval = self.get_interval() - (timestamp - last_run)
                    self.helper.log_info(
                        f"Connector will run in: {new_interval} seconds"
                    )
                time.sleep(60)

            except (KeyboardInterrupt, SystemExit):
                self.helper.log_info("Connector stopped.")
                exit(0)
            except Exception as ex:
                self.helper.log_error(str(ex))
                time.sleep(60)


if __name__ == "__main__":
    try:
        sftp_receiver = SftpReceiver()
        sftp_receiver.run()
    except Exception as ex:
        self.helper.log_error(str(ex))
        time.sleep(10)
        exit(0)
