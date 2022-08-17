#!/usr/bin/env python3
import configparser
import logging
import time

from . import messaging

{% if asyncapi.components() -%}
{% for schemaName, schema in asyncapi.components().schemas() -%}
{% set moduleName = schemaName | lowerFirst -%}
from .{{ moduleName }} import {{ schemaName | upperFirst }}
{% endfor -%}
{% else -%}
from .payload import Payload
{% endif %}


# Config has the connection properties.
def getConfig():
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    config = config_parser['DEFAULT']
    return config

{% for channelName, channel in asyncapi.channels() -%}
{% set sub = [asyncapi.info(), params, channel] | getRealSubscriber -%}
{%- if sub -%}
{%- set functionName = [channelName, channel] | functionName -%}
{%- set payloadClass = sub | payloadClass -%}
{%- set varName =  payloadClass | lowerFirst %}
def {{ functionName }}(client, userdata, msg):
    jsonString = msg.payload.decode('utf-8')
    logging.info('Received json: ' + jsonString)
    {{ varName }} = {{ payloadClass }}.from_json(jsonString)
    logging.info('Received message: ' + str({{ varName }}))
{% endif %}
{% endfor %}

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Start of main.')
    config = getConfig()
{% set publishMessenger = [params, asyncapi] | getFirstPublisherMessenger -%}
{% set messengers = [params, asyncapi] | getMessengers -%}
{%- for messenger in messengers -%}
{%- if messenger.subscribeTopic %}
    {{ messenger.name }} = messaging.Messaging(config, '{{ messenger.subscribeTopic }}', {{ messenger.functionName }})
{%- else %}
    {{ messenger.name }} = messaging.Messaging(config)
{%- endif %}
{%- if publishMessenger %}
    {{ messenger.name }}.loop_start()
{%- else %}
    {{ messenger.name }}.loop_forever()
{%- endif %}
{%- endfor %}
{%- if publishMessenger %}

    # Example of how to publish a message. You will have to add arguments to the constructor on the next line:
    payload = {{ publishMessenger.payloadClass }}()
    payload_json = payload.to_json()

    while (True):
        {{ publishMessenger.name }}.publish('{{ publishMessenger.publishTopic }}', payload_json)
        time.sleep(1)
{%- endif %}

if __name__ == '__main__':
    main()

