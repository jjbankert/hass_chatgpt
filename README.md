# Notice: Project Discontinued
This project will no longer be maintained. The [responding services](https://www.home-assistant.io/blog/2023/07/05/release-20237/#services-can-now-respond) feature in Home Assistant's 2023.7 release enables me to use the [OpenAI Conversation integration](https://www.home-assistant.io/integrations/openai_conversation/) for all my personal use cases. 

Thanks to everyone who responded with issues, pull requests and on the Home Assistant community thread.

See further down for the original documentation.

I'll show here how you can modify [Example 2: Single Automation](#example-2-single-automation) to use the new native feature. It's overall much simpler than before, which is nice. The only tricky thing is figuring out the `agent_id`. Go to developer tools -> services -> `conversation.process`. In the UI mode, select your OpenAI conversation agent from the Agent drop-down, and then switch to YAML mode to see the id.

```yaml
alias: Say With ChatGPT
trigger:
  - platform: event
    event_type: your_trigger_event_type
action:
  - service: conversation.process
    data:
      agent_id: <agent_id goes here>
      text: Write a happy, one line, spoken language reminder for the 'cleaning' calendar event.
    response_variable: chatgpt
  - service: notify.mobile_app_<your_device_id_here>
    data:
      message: TTS
      data:
        tts_text: "{{chatgpt.response.speech.plain.speech | trim | replace('\"','')}}"
```

# ChatGPT Integration for Home Assistant
This is a custom integration for Home Assistant that allows you to interact with OpenAI's ChatGPT API. The source code can be found on [GitHub](https://github.com/jjbankert/hass_chatgpt).

Note that this is not an official integration, and so not developed by either OpenAI or Home Assistant/Nabu Casa.

- [Notice: Project Discontinued](#notice-project-discontinued)
- [ChatGPT Integration for Home Assistant](#chatgpt-integration-for-home-assistant)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Method 1: HACS](#method-1-hacs)
    - [Method 2: Manual Installation](#method-2-manual-installation)
    - [Configuration](#configuration)
  - [Usage](#usage)
    - [Service](#service)
    - [Example 1: Two Automations](#example-1-two-automations)
    - [Example 2: Single Automation](#example-2-single-automation)

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
- `callback_event` (optional): The event type that is used for the response event that contains the chat data. By default, this is `return_value`, but something like `chatgpt_tts` might make sense for the subset of responses that should be picked up by a TTS automation.
- `callback_id` (optional): A unique identifier that makes it easy to pick the response to the service call from the `return_value` events. In automations, `{{this.context.id}}` works well.

The service call response will be sent as a return_value event or the custom event type specified in the callback_event parameter. The event data will contain the ChatGPT response as [defined here](https://platform.openai.com/docs/api-reference/chat). Currently this is a `content` key with the response message, and the `"role": "assistant"` pair. If `callback_id` is set in the request, the response `event.data.callback_id` will contain the same value.

See the examples below for practical examples.

### Example 1: Two Automations

This example demonstrates how to use the `chatgpt.chat` service with two separate automations. The first automation calls the service, and the second automation is triggered by the resulting event defined in the `callback_event` parameter.

**Pros:**
* This is relatively simple to set up, compared to putting all the logic in a single automation.
* Also it can be nice to unify all the TTS logic in a single automation.

**Cons:**
* It's harder to customize the 'Handle ChatGPT Response' automation based on the original event that triggered the 'Request GPT Response' Automation. For example you might want to used different groups of TTS devices for different use-cases.

**Automation 1:** Call the Service

```yaml
alias: Request ChatGPT Response
trigger:
  - platform: event
    event_type: your_trigger_event_type
action:
  - service: chatgpt.chat
    data:
      messages:
        - role: user
          content: 'Write a happy, one line, spoken language reminder for the cleaning calendar event.'
      callback_event: chatgpt_tts
```

**Automation 2:** Handle the Response
In this example the response is handled by using the [Android app's](https://companion.home-assistant.io/docs/notifications/notifications-basic/#text-to-speech-notifications) text-to-speech functionality.

```yaml
alias: Handle ChatGPT Response
trigger:
  - platform: event
    event_type: chatgpt_tts
action:
  - service: notify.mobile_app_<your_device_id_here>
    data:
      message: TTS
      data:
        tts_text: "{{trigger.event.data.content | trim | replace('\"','')}}"
```

### Example 2: Single Automation

This example demonstrates how to use the `chatgpt.chat` service to generate a response and send it to a TTS device within a single automation. It is triggered by an event of your choice and sends the generated response to an [Android device]() for text-to-speech.

The example automation uses the `parallel` option to execute two sequences simultaneously, ensuring that the listener is set up before the response is generated. The `callback_id` is used to match the response event with the correct service call.

- **call chatgpt**: The first sequence introduces a 100ms delay before calling the `chatgpt.chat` service. This delay is included to ensure that the listener in the second sequence is set up and ready to receive the response from ChatGPT. The callback_id is set to `{{this.context.id}}` to uniquely identify the response event.
- **call tts**: The second sequence waits for a `return_value` event with a matching `callback_id`. When the event is received, it extracts the content of the response message and sends it to the TTS device. Note that I added some post-processing of the result with `trim` and `replace`, because the ChatGPT output can be a bit inconsistent.


**Pros:**
* It's easy to customize exactly how the response is handled, based on the event that triggers 'Say With ChatGPT'
* Text-to-speech logic can be unified in a more flexible script that you can pass targets to.

**Cons:**
* The logic is kind of hard to understand and inelegant. Home Assistant doesn't have specific logic to grab a service's output in the same automation that called the service, and so we make do with what we got.

```yaml
alias: Say With ChatGPT
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
