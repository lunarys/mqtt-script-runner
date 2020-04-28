import yaml
import os
import paho.mqtt.client as mqtt
import sys
import signal


#####################################################
def on_message(client, usr, msg):
    message = msg.payload.decode("utf-8")
    topic = msg.topic
    print("[R] Received", message, "on", topic)
    script = config.get(topic, {}).get(message)
    if script is None:
        print("[N] Message not configured, doing nothing")
    else:
        if isinstance(script, dict):
            command = script.get("script")
            status = script.get("status", {})
            status_topic = status.get("topic")
            status_success = status.get("onSuccess")
            status_failed = status.get("onFailure")
            status_retained = status.get("retained", False)
            if command is not None:
                print("[S] Running:", command)
                exit_status = os.system(command)
                if exit_status == 0:
                    print("    Execution success")
                    if status_success is not None:
                        print("    Publishing", status_success, "on", status_topic)
                        client.publish(status_topic, status_success, qos, status_retained)
                elif exit_status > 0:
                    print("    Execution failure")
                    if status_failed is not None:
                        print("    Publishing", status_failed, "on", status_topic)
                        client.publish(status_topic, status_failed, qos, status_retained)
        elif isinstance(script, str):
            print("[S] Running:", script)
            os.system(script)


#####################################################
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscription")


#####################################################
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("[C] Connected OK")
        # Iterate through all keys (topic) of the config entries and set up listener
        for topic in [*config]:
            print("[T] Subscribing to topic", topic)
            result = client.subscribe(topic, qos)
    else:
        print("[C] Bad connection: Returned code=", rc)


#####################################################
def on_disconnect(client, userdata, rc):
    print("[C] Disconnected: ", rc)
    client.connected_flag = False


#####################################################
def interrupt_handler(sig, frame):
    print("Received interrupt, terminating...")
    client.disconnect()
    exit()


#####################################################

# Listen to interrupt and termination
signal.signal(signal.SIGINT, interrupt_handler)
signal.signal(signal.SIGTERM, interrupt_handler)

# Set default values
broker_address = "localhost"
port = 1883
qos = 1
config_file = "config-example.yaml"

# Get iterator for command line arguments and skip first item (script call)
arg_it = iter(sys.argv)
next(arg_it)

user_set = False
password_set = False

# Parse environment variables
broker_address = os.getenv('MQTT_BROKER', broker_address)
port = int(os.getenv('MQTT_PORT', port))
qos = int(os.getenv('MQTT_QOS', qos))
user = os.environ.get('MQTT_USER')
password = os.environ.get('MQTT_PASSWORD')

if user is not None:
    user_set = True

if password is not None:
    password_set = True

# Parse command line arguments
for arg in arg_it:
    if arg == '-a':
        broker_address = next(arg_it)

    elif arg == '-q':
        qos = next(arg_it)

    elif arg == '-c':
        config_file = next(arg_it)

    elif arg == '-p':
        port = next(arg_it)

    elif arg == '-u':
        user = next(arg_it)
        user_set = True

    elif arg == '-pw' or arg == '-P':
        password = next(arg_it)
        password_set = True

    elif arg == '-f':
        import configparser

        configParser = configparser.RawConfigParser()
        configParser.read(next(arg_it))

        if configParser.has_option('settings', 'address'):
            broker_address = configParser.get('settings', 'address')

        if configParser.has_option('settings', 'qos'):
            qos = configParser.getint('settings', 'qos')

        if configParser.has_option('settings', 'config_file'):
            config_file = configParser.get('settings', 'config_file')

        if configParser.has_option('settings', 'port'):
            port = configParser.getint('settings', 'port')

        if configParser.has_option('settings', 'user'):
            user = configParser.get('settings', 'user')
            user_set = True

        if configParser.has_option('settings', 'password'):
            password = configParser.get('settings', 'password')
            password_set = True

    elif arg == '-h':
        print("Usage:", sys.argv[0],
              "[-f <broker-config-file>] [-a <ip>] [-p <port>] [-q <qos>] [-u <username>] [-pw <password>] [-c <listener-config-file>]")
        exit()

    else:
        print("Use \'", sys.argv[0], " -h\' to print available arguments.")
        exit()

# User and password need to be set both or none
if user_set != password_set:
    print("Please set either both username and password or none of those")
    exit()

# Read config file into variable config
stream = open(config_file, 'r')
config = yaml.safe_load(stream)
stream.close()

# Set up MQTT client
client = mqtt.Client()
# Set callback functions
client.on_message = on_message
# client.on_subscribe = on_subscribe
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Set username and password
if user_set and password_set:
    client.username_pw_set(user, password)

# Connect to broker
client.connect(broker_address, port)
# Start client loop (automatically reconnects after connection loss)
client.loop_forever()
