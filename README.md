# Sp3-Server
This repository is a local server, which can handle Tenda-Beli SP3 Smart Plugs.
It is based on the research made by Gough Lui (https://goughlui.com/2020/02/22/reverse-engineer-tenda-beli-sp3-smart-wi-fi-plug-protocol/) and his 
Python server implementation (https://goughlui.com/2020/08/13/project-simple-python-based-controller-for-tenda-beli-sp3-smart-wi-fi-plugs/)

# Notes:
- This server is largely redundant, as each plug has be controlled by its internal RestFul API.
   - GET http://{PlugIP}:5000/getSta - Gets the current state of the plug
   - POST http://{PlugIP}:5000/setSta - Sets the plug to the new state (1 = on, 0 = off)
      - Payload: {"State": {TargetState}}

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

1. Clone the repository and navigate to the project directory:
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:

   ```bash
   python main.py
   ```

2. Open your browser and visit `http://localhost:3000` to view the application.