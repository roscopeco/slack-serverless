from typing import Any

import requests

EPHEMERAL = "ephemeral"
IN_CHANNEL = "in_channel"


def slack_post_message(
    slack_access_token: str,
    channel: str,
    text: str,
    endpoint: str = "https://slack.com/api/chat.postMessage",
) -> bool:
    """
    Post an immediate simple text message to slack.

    :param slack_access_token: The bot access token (from your Slack app settings).
    :param channel: The channel to post to.
    :param text: The message text.
    :param endpoint: (Optional) use a different Slack endpoint.
    :return: True if success, False otherwise.
    """
    response = requests.post(
        endpoint,
        json={"channel": channel, "text": text},
        headers={"Authorization": f"Bearer {slack_access_token}"},
    )

    return response.status_code == 200


def slack_ephemeral_text_response(text: str) -> dict[str, str]:
    """
    Build an ephemeral Slack response with the given simple text.

    :param text: The message text.
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(EPHEMERAL, {"text": text})


def slack_ephemeral_blocks_response(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build an ephemeral Slack response with the given content blocks.

    :param blocks: The message content blocks.
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(EPHEMERAL, {"blocks": blocks})


def slack_in_channel_text_response(text: str) -> dict[str, str]:
    """
    Build an in-channel Slack response with the given simple text.

    :param text: The message text.
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(IN_CHANNEL, {"text": text})


def slack_in_channel_blocks_response(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build an in-channel Slack response with the given content blocks.

    :param blocks: The message content blocks.
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(IN_CHANNEL, {"blocks": blocks})


def slack_message_response(
    response_type: str, content: dict[str, Any]
) -> dict[str, str]:
    """
    Build a Slack response with the given response type and content.

    :param response_type: Response type ('ephemeral' or 'in_channel').
    :param content: A dict containing either {"text": text} or {"blocks": blocks}.
    :return: The response body for conversion to JSON.
    """
    if response_type not in [EPHEMERAL, IN_CHANNEL]:
        raise ValueError(f"Unrecognised response_type: {response_type}")

    return {"response_type": response_type, **content}


def slack_tags(user_ids: list[str], separator: str = " ") -> str:
    """
    Generate a separated list of Slack content markup elements to tag the given user IDs.

    :param user_ids: The list of user IDs for tagging.
    :param separator: The separator (defaults to space).
    :return: The list of markup tags.
    """
    return separator.join([f"<@{user_id}>" for user_id in user_ids])
