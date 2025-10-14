# OREI HDMI Matrix Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A Home Assistant integration for controlling OREI 8x8 HDMI matrix switches via their web interface.

## Features

- **8x8 Matrix Support**: Control all 8 outputs and 8 inputs
- **Real-time Status**: Monitor current input/output mappings
- **Easy Configuration**: Simple setup through Home Assistant's UI
- **Select Entities**: Use dropdown selectors to choose inputs for each output
- **Auto-discovery**: Automatically detects input and output names from the device

## Supported Devices

This integration is designed for OREI 8x8 HDMI matrix switches with web interface support. It has been tested with models that use the `/cgi-bin/instr` API endpoint.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add this repository URL: `https://github.com/skroged/hass-orei-hdmi-matrix`
5. Select "Integration" as the category
6. Click "Add"
7. Find "OREI HDMI Matrix" in the integrations list and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/skroged/hass-orei-hdmi-matrix/releases) page
2. Extract the `custom_components` folder to your Home Assistant configuration directory
3. Restart Home Assistant

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "OREI HDMI Matrix"
4. Enter your device details:
   - **Host/IP Address**: The IP address of your HDMI matrix (e.g., `192.168.1.100`)
   - **Username**: Usually `Admin` (default)
   - **Password**: Usually `admin` (default)

### Configuring Inputs and Outputs

After the initial setup, you can configure your inputs and outputs:

1. Go to **Settings** → **Devices & Services**
2. Find your OREI HDMI Matrix integration
3. Click the **Configure** button (gear icon)
4. Configure each input and output:
   - **Input Names**: Give meaningful names to your inputs (e.g., "Living Room Apple TV", "Gaming Console", "Cable Box")
   - **Output Names**: Name your outputs (e.g., "Living Room TV", "Bedroom TV", "Office Monitor")
   - **Output Enabled**: Enable/disable outputs you don't want to control

### Input/Output Configuration

- **Inputs**: Each of the 8 inputs can be given a custom name to make them easier to identify
- **Outputs**: Each of the 8 outputs can be:
  - Given a custom name
  - Enabled or disabled (disabled outputs won't appear as entities)
  - Configured to show only specific inputs (all inputs available by default)

## Usage

After configuration, you'll have select entities created for each enabled output:

- `select.living_room_tv_input` - Choose input for Living Room TV (if you named Output 1 "Living Room TV")
- `select.bedroom_tv_input` - Choose input for Bedroom TV (if you named Output 2 "Bedroom TV")
- ... and so on for all enabled outputs

Each select entity will show the available inputs with their configured names and allow you to change which input is connected to that output.

### Device Organization

Each output appears as its own device in Home Assistant, making it easy to:
- Organize in dashboards by room or location
- Create automations specific to each display
- Control individual outputs independently

### Example Automation

```yaml
automation:
  - alias: "Switch Living Room TV to Gaming Console"
    trigger:
      platform: state
      entity_id: input_boolean.gaming_mode
      to: 'on'
    action:
      service: select.select_option
      target:
        entity_id: select.living_room_tv_input
      data:
        option: "Gaming Console"  # Using the configured input name
```

### Example Script

```yaml
script:
  switch_to_movie_night:
    alias: "Movie Night Setup"
    sequence:
      - service: select.select_option
        target:
          entity_id: select.living_room_tv_input
        data:
          option: "Apple TV"  # Using configured input name
      - service: select.select_option
        target:
          entity_id: select.bedroom_tv_input
        data:
          option: "Apple TV"  # Using configured input name
```

## API Details

This integration communicates with the OREI HDMI matrix using HTTP POST requests to the `/cgi-bin/instr` endpoint:

- **Authentication**: `{"comhead":"login","user":"Admin","password":"admin"}`
- **Get Status**: `{"comhead":"get video status","language":0}`
- **Switch Input**: `{"comhead":"video switch","language":0,"source":[output,input]}`

## Troubleshooting

### Connection Issues

- Verify the IP address is correct and the device is reachable
- Check that the web interface is accessible in a browser
- Ensure the username and password are correct (default: Admin/admin)

### Entity Not Updating

- Check the Home Assistant logs for any error messages
- Verify the device is responding to API calls
- Try restarting the integration

### Authentication Errors

- Some devices may have different default credentials
- Check the device's web interface for the correct username/password
- Some devices may require factory reset to restore default credentials

## Development

### Setting up Development Environment

1. Clone this repository
2. Copy the `custom_components` folder to your Home Assistant configuration
3. Restart Home Assistant
4. Make changes and test

### Running Tests

```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Home Assistant community for the excellent integration framework
- Special thanks to OREI for making HDMI matrix switches with web interfaces
