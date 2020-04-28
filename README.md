# mqtt-script-runner

I created this docker image to run arbitrary shell scripts for messages on MQTT topics. This is a base image that can be extended to include the necessary scripts for whatever you want to do with it.

## Broker configuration

The broker to connect to can either be configured using environment variables, by using a configuration file or command line options.
The easiest way is probably using environment variables, as this does not require changes to the command executed in the docker container.

Command line options overwrite environment variables and the configuration file overwrites options defined before the file (using `-f`).

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| MQTT_BROKER | localhost | The MQTT broker address |
| MQTT_PORT | 1883 | The port of the MQTT broker |
| MQTT_QOS | 1 | The quality of service for MQTT |
| MQTT_USER | | The username for the MQTT broker |
| MQTT_PASSWORD | | The password for the MQTT user |

### Configuration file

```
[settings]
address = localhost
port = 1883
qos = 1
user = user
password = hackme
config_file = /src/mqtt/scripts.yaml
```

### Command line options

| Option | Default   | Description |
|:------:|-----------|-------------|
| -a     | localhost | The MQTT broker address |
| -p     | 1883      | The port of the MQTT broker |
| -q     | 1         | The quality of service for MQTT |
| -u     |           | The username for the MQTT broker |
| -P     |           | The password for the MQTT user |
| -c     |           | The configuration file for scripts |
| -f     |           | The configuration file for the MQTT broker |

## Script configuration

The scripts are configured in a `.yaml` file, grouped by topics. This file is included in the container as `/src/mqtt/scripts.yaml` by default.

The following configuration example is slightly changed from a container I use to switch on and off the wifi on a FritzBox.

```yaml
device/router/wifi/desired:                                   # The topic
  "ON":                                                       # The message
    script: "sh /src/fritz/fritz.sh ON /src/fritz/fritz.conf" # The script to run
    status:
      topic: "device/router/wifi"                             # The topic to send the result on
      onSuccess: "ON"                                         # The message to publish in case of success
      onFailure: "FAILED"                                     # The message to publish in case of failure
      retained: False                                         # If the status message should be retained or not
  "OFF": 
    script: "sh /src/fritz/fritz.sh OFF /src/fritz/fritz.conf"
    status:
      topic: "device/router/wifi"
      onSuccess: "OFF"
example/test:
  "hello": "echo Hello World!"                                # Short form in case status is not required
```
