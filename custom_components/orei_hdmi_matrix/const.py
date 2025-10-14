"""Constants for the OREI HDMI Matrix integration."""
from datetime import timedelta

DOMAIN = "orei_hdmi_matrix"

# Configuration keys
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_INPUTS = "inputs"
CONF_OUTPUTS = "outputs"
CONF_NAME = "name"
CONF_ENABLED = "enabled"
CONF_AVAILABLE_INPUTS = "available_inputs"
CONF_INPUT_ENABLED = "input_enabled"

# Default values
DEFAULT_USERNAME = "Admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_TIMEOUT = 10

# API endpoints
API_ENDPOINT = "/cgi-bin/instr"

# API commands
CMD_LOGIN = "login"
CMD_GET_STATUS = "get video status"
CMD_VIDEO_SWITCH = "video switch"

# Matrix configuration
NUM_INPUTS = 8
NUM_OUTPUTS = 8

# Update intervals
UPDATE_INTERVAL = timedelta(seconds=30)
