# ChatGPT Integration for Home Assistant

This is a custom integration for Home Assistant that allows you to interact with OpenAI's ChatGPT API. The source code can be found on [GitHub](https://github.com/jjbankert/hass_chatgpt).

Note that this is not an official integration, and so not developed by either OpenAI or Home Assistant/Nabu Casa.

- [ChatGPT Integration for Home Assistant](#chatgpt-integration-for-home-assistant)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Method 1: HACS](#method-1-hacs)
    - [Method 2: Manual Installation](#method-2-manual-installation)
    - [Configuration](#configuration)
  - [Usage](#usage)
    - [Service](#service)
    - [Example Home Assistant Automation](#example-home-assistant-automation)

## Prerequisites

Before installing the ChatGPT integration, you need to have an account on [platform.openai.com](https://platform.openai.com/) and generate an API key. To retrieve the API key you'll use in your requests, visit your [API keys page](https://platform.openai.com/account/api-keys).

When you sign up, you'll receive $5 in credit to start experimenting with the ChatGPT integration. This credit can be used during your first 3 months.
After that the ChatGPT integration will incur costs based on the model and usage. As of now, the default model `gpt-3.5-turbo` costs $0.002 per 1K tokens, but you can check the [OpenAI pricing page](https://openai.com/pricing) for up-to-date information and additional models.

Keep in mind that both input and output tokens count toward this usage. 

## Installation

There are two methods to install this integration, each with its own update process:

- **HACS**: Offers a user-friendly interface to install and update custom integrations. When an update is available, it will be displayed within HACS for easy updating.
- **Manual**: Requires you to manually download and replace the integration files from the GitHub repository. You'll need to periodically check the repository for updates and manually apply them.

### Method 1: HACS

1. Open Home Assistant Community Store (HACS) in Home Assistant.
2. Go to the "Integrations" tab.
3. Click on the three dots in the upper right corner and select "Custom repositories."
4. Add `https://github.com/jjbankert/hass_chatgpt` as a custom repository with the category "Integration."
5. Click "Add."
6. Search for "ChatGPT" in the "Integrations" tab and click "Install."
7. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the `chatgpt` folder from the [GitHub repository](https://github.com/jjbankert/hass_chatgpt) and copy it to the `custom_components` folder in your Home Assistant configuration directory.
2. Restart Home Assistant.

### Configuration

After installing the integration using either method, add the following configuration to your `configuration.yaml` file:

```yaml
chatgpt:
  api_key: YOUR_API_KEY
  model: gpt-3.5-turbo # optional, default is "gpt-3.5-turbo"
  temperature: 1.0 # optional, default is 1.0
```

Lastly, restart Home Assistant again, or reload all YAMLs in the Developer Tools.

## Usage

### Service

The integration provides a `chatgpt.chat` service that takes the following parameters:

- `messages` (required): The messages (chat history) for ChatGPT. See [OpenAI API documentation](https://platform.openai.com/docs/guides/chat) for more details.
- `callback_id` (optional): A unique identifier that makes it easy to pick the response to the service call from the `return_value` events. In automations, `{{this.context.id}}` works well.

The service call response will be sent as a `return_value` event. The event data will contain the ChatGPT response as [defined here](https://platform.openai.com/docs/api-reference/chat). Currently this is a `content` key with the response message, and the `"role": "assistant"` pair. If `callback_id` is set in the request, the response `event.data.callback_id` will contain the same value.

See the example below for a practical example.

### Example Home Assistant Automation

Here's an example automation that demonstrates how to use the `chatgpt.chat` service to generate a response and send it to a TTS device.

This example is triggered by an event of your choice. It generates a response from ChatGPT based on the input message and sends it to an [Android device](https://companion.home-assistant.io/docs/notifications/notifications-basic/#text-to-speech-notifications) for text-to-speech. The automation consists of two parallel sequences:

The example uses the `parallel` option to execute two sequences simultaneously, ensuring that the listener is set up before the response is generated. It also demonstrates how to use the `callback_id` to match the response event with the correct service call.

- **call chatgpt**: The first sequence introduces a 100ms delay before calling the `chatgpt.chat` service. This delay is included to ensure that the listener in the second sequence is set up and ready to receive the response from ChatGPT. The callback_id is set to `{{this.context.id}}` to uniquely identify the response event.
- **call tts**: The second sequence waits for a `return_value` event with a matching `callback_id`. When the event is received, it extracts the content of the response message and sends it to the TTS device. Note that I added some post-processing of the result with `trim` and `replace`, because the ChatGPT output can be a bit inconsistent.

```yaml
alias: Say With GPT
trigger:
  - platform: event
    event_type: your_trigger_event_type
action:
  - parallel:
      - alias: call chatgpt
        sequence:
          - delay:
              hours: 0
              minutes: 0
              seconds: 0
              milliseconds: 100
          - service: chatgpt.chat
            data:
              messages:
                - role: user
                  content: 'Write a happy, one line, spoken language reminder for the cleaning calendar event.'
              callback_id: "{{this.context.id}}"
      - alias: call tts
        sequence:
          - wait_for_trigger:
              - platform: event
                event_type: return_value
                event_data:
                  callback_id: "{{this.context.id}}"
            timeout:
              hours: 0
              minutes: 1
              seconds: 0
              milliseconds: 0
            continue_on_timeout: false
          - service: notify.mobile_app_<your_device_id_here>
            data:
              message: TTS
              data:
                tts_text: "{{wait.trigger.event.data.content | trim | replace('\"','')}}"
```
