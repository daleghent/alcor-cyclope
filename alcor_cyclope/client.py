import socket
import re
import datetime
from zoneinfo import ZoneInfo

class AlcorCyclopeClient:
    """
    A client for communicating with the Alcor Cyclope TCP service.

    This client establishes a socket connection to the server,
    sends commands, and parses responses related to measurement data and system status.
    """

    def __init__(self, host, port=45789):
        """
        Initialize the client with the specified host and port.

        Args:
            host (str): The hostname or IP address of the server.
            port (int, optional): The port number to connect to. Default is 45789.
        """
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """
        Establish a connection to the server.

        Raises:
            ConnectionError: If the connection fails or the server response is unexpected.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.host, self.port))

        # Read the greeting banner
        banner = self._recv_line()
        if not banner.startswith("200 - OK"):
            raise ConnectionError(f"Unexpected server response: {banner}")

    def _recv_line(self):
        """
        Receive a single line of response from the socket.

        Returns:
            str: The received line as a decoded string.
        """
        data = b""
        while not data.endswith(b"\n"):
            chunk = self.socket.recv(1)
            if not chunk:
                break
            data += chunk
        return data.decode().strip()

    def send_command(self, command):
        """
        Send a command to the server and receive a response.

        Args:
            command (str): The command string to send.

        Returns:
            list[str]: A list of response lines from the server.

        Raises:
            ConnectionError: If there is no active connection.
            RuntimeError: If the server response is unexpected.
        """
        if not self.socket:
            raise ConnectionError("Not connected to the server.")

        self.socket.sendall((command + "\n").encode())
        status_line = self._recv_line()
        if not status_line.startswith("201"):
            raise RuntimeError(f"Unexpected response: {status_line}")

        # Read response body until a line containing only '.'
        response_lines = []
        while True:
            line = self._recv_line()
            if line == ".":
                break
            response_lines.append(line)

        return response_lines

    def get_data(self):
        """
        Request measurement data from the server.

        Returns:
            dict: A dictionary containing measurement data with keys like:
                - valid (bool)
                - measurement_jd_utc (float)
                - measurement_date_utc (datetime)
                - measurement_jd_local (float)
                - measurement_date_local (datetime)
                - last_zenith_arcsec (float)
                - last_r0_arcsec (float)
        """
        response = self.send_command("SysRequest <GetData>")
        data = {}

        for line in response:
            match = re.match(r"<(.*?)=(.*?)>", line)
            if match:
                key, value = match.groups()
                match key:
                    case "IS_Valid":
                        name = "valid"
                        try:
                            data[name] = bool(value)
                        except ValueError:
                            data[name] = None

                    case "UTC_DateMeasurement":
                        name = "measurement_jd_utc"
                        try:
                            data[name] = float(value)
                        except ValueError:
                            data[name] = None

                    case "UTC_DateMeasurement_Readable":
                        name = "measurement_date_utc"
                        try:
                            time = datetime.datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p")
                            data[name] = time.replace(tzinfo=ZoneInfo('Etc/UTC'))
                        except ValueError:
                            data[name] = None

                    case "LCL_DateMeasurement":
                        name = "measurement_jd_local"
                        try:
                            data[name] = float(value)
                        except ValueError:
                            data[name] = None

                    case "LCL_DateMeasurement_Readable":
                        name = "measurement_date_local"
                        try:
                            data[name] = datetime.datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p")
                        except ValueError:
                            data[name] = None

                    case "Last_ZenithArcsec":
                        name = "last_zenith_arcsec"
                        try:
                            data[name] = float(value)
                        except ValueError:
                            data[name] = None

                    case "Last_R0Arcsed":
                        name = "last_r0_arcsec"
                        try:
                            data[name] = float(value)
                        except ValueError:
                            data[name] = None

                    case _:  # Default case (if key does not match any known value)
                        pass

        return data

    def get_status(self):
        """
        Retrieve the current status code of the Cyclope system.

        Returns:
            int: The system status code, where:
                - 0: Unknown
                - 1: Idle
                - 2: Idle (Daytime)
                - 3: Seeking for star
                - 4: Measuring
                - 5: Star Lost
        """
        response = self.send_command("SysRequest <SysStatus>")

        for line in response:
            match = re.match(r"<State=.*?\|(\d)>", line)
            if match:
                return int(match.group(1))

        return 0  # Default to Unknown

    def translate_status(self, status_code):
        """
        Convert a status code into a human-readable string.

        Args:
            status_code (int): The numerical status code.

        Returns:
            str: A descriptive status string.
        """
        status_map = {
            0: "Unknown",
            1: "Idle",
            2: "Idle (Daytime)",
            3: "Seeking for star",
            4: "Measuring",
            5: "Star Lost"
        }
        return status_map.get(status_code, "Unknown")

    def close(self):
        """
        Close the socket connection to the server.
        """
        if self.socket:
            self.socket.close()
            self.socket = None
