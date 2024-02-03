from typing import Any

import requests

EPHEMERAL = "ephemeral"
IN_CHANNEL = "in_channel"


def slack_post_message(
    slack_access_token: str,
    channel: str,
    message: dict[str, Any],
    endpoint: str = "https://slack.com/api/chat.postMessage",
) -> bool:
    """
    Post an immediate message to slack with any parameters.

    :param slack_access_token: The bot access token (from your Slack app settings).
    :param channel: The channel to post to.
    :param message: Message parameters for Slack (should include at least 'text' or 'blocks'!)
    :param endpoint: (Optional) use a different Slack endpoint.
    :return: True if success, False otherwise.
    """
    response = requests.post(
        endpoint,
        json={**{"channel": channel}, **message},
        headers={"Authorization": f"Bearer {slack_access_token}"},
    )

    return response.status_code == 200


def slack_post_text_message(
    slack_access_token: str,
    channel: str,
    text: str,
    params: dict[str, Any] = None,
    endpoint: str = "https://slack.com/api/chat.postMessage",
) -> bool:
    """
    Post an immediate simple text message to slack.

    :param slack_access_token: The bot access token (from your Slack app settings).
    :param channel: The channel to post to.
    :param text: The message text.
    :param params: (Optional) additional parameters for Slack
    :param endpoint: (Optional) use a different Slack endpoint.
    :return: True if success, False otherwise.
    """
    return slack_post_message(
        slack_access_token=slack_access_token,
        channel=channel,
        message={**{"text": text}, **(params or {})},
        endpoint=endpoint,
    )


def slack_post_blocks_message(
    slack_access_token: str,
    channel: str,
    blocks: dict[str, Any],
    params: dict[str, Any] = None,
    endpoint: str = "https://slack.com/api/chat.postMessage",
) -> bool:
    """
    Post an immediate blocks message to slack.

    :param slack_access_token: The bot access token (from your Slack app settings).
    :param channel: The channel to post to.
    :param blocks: The message blocks.
    :param params: (Optional) additional parameters for Slack
    :param endpoint: (Optional) use a different Slack endpoint.
    :return: True if success, False otherwise.
    """
    return slack_post_message(
        slack_access_token=slack_access_token,
        channel=channel,
        message={**{"blocks": blocks}, **(params or {})},
        endpoint=endpoint,
    )


def slack_ephemeral_text_response(
    text: str, params: dict[str, Any] = None
) -> dict[str, str]:
    """
    Build an ephemeral Slack response with the given simple text.

    :param text: The message text.
    :param params: (Optional) additional Slack parameters
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(EPHEMERAL, {"text": text}, params)


def slack_ephemeral_blocks_response(
    blocks: list[dict[str, Any]], params: dict[str, Any] = None
) -> dict[str, Any]:
    """
    Build an ephemeral Slack response with the given content blocks.

    :param blocks: The message content blocks.
    :param params: (Optional) additional Slack parameters
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(EPHEMERAL, {"blocks": blocks}, params)


def slack_in_channel_text_response(
    text: str, params: dict[str, Any] = None
) -> dict[str, str]:
    """
    Build an in-channel Slack response with the given simple text.

    :param text: The message text.
    :param params: (Optional) additional Slack parameters
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(IN_CHANNEL, {"text": text}, params)


def slack_in_channel_blocks_response(
    blocks: list[dict[str, Any]], params: dict[str, Any] = None
) -> dict[str, Any]:
    """
    Build an in-channel Slack response with the given content blocks.

    :param blocks: The message content blocks.
    :param params: (Optional) additional Slack parameters
    :return: The response body for conversion to JSON.
    """
    return slack_message_response(IN_CHANNEL, {"blocks": blocks}, params)


def slack_message_response(
    response_type: str, content: dict[str, Any], params: dict[str, Any] = None
) -> dict[str, str]:
    """
    Build a Slack response with the given response type and content.

    :param response_type: Response type ('ephemeral' or 'in_channel').
    :param content: A dict containing either {"text": text} or {"blocks": blocks}.
    :param params: (Optional) additional Slack parameters
    :return: The response body for conversion to JSON.
    """
    if response_type not in [EPHEMERAL, IN_CHANNEL]:
        raise ValueError(f"Unrecognised response_type: {response_type}")

    return {"response_type": response_type, **content, **(params or {})}


def slack_tags(user_ids: list[str], separator: str = " ") -> str:
    """
    Generate a separated list of Slack content markup elements to tag the given user IDs.

    :param user_ids: The list of user IDs for tagging.
    :param separator: The separator (defaults to space).
    :return: The list of markup tags.
    """
    return separator.join([f"<@{user_id}>" for user_id in (user_ids or [])])
