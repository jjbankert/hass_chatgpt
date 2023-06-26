"""ChatGPT Integration"""
import requests
import logging

from homeassistant.core import Config, HomeAssistant, ServiceCall, Context

_LOGGER = logging.getLogger(__name__)

DOMAIN = "chatgpt"

def setup(hass: HomeAssistant, config: Config):
    def chat(call: ServiceCall):
        # load the call parameters
        messages = call.data["messages"]
        callback_id = call.data.get("callback_id", None)
        callback_event = call.data.get("callback_event", "return_value")

        # load the config
        static_conf = config[DOMAIN]
        api_key = static_conf["api_key"]
        model = static_conf.get("model", "gpt-3.5-turbo")
        temperature = static_conf.get("temperature", 1.0)

        # make the request
        # timeout 3.2s to connect (1 retry), 60s to generate the answer
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "temperature": temperature},
            timeout=(3.2, 60),
        )

        # prepare the result
        _LOGGER.debug('chatgpt - API response: %s', response.json() )
        response_msg = response.json()["choices"][0]["message"]
        if callback_id is not None:
            response_msg["callback_id"] = callback_id

        # return the result
        hass.bus.fire(callback_event, response_msg)

    hass.services.register(DOMAIN, "chat", chat)

    # Return boolean to indicate that initialization was successful.
    return True
