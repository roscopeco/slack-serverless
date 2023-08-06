import base64
import json
from concurrent.futures import CancelledError
from typing import Callable, Any

import requests
from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsub_v1.publisher.exceptions import MessageTooLargeError
from requests import Response


def slack_defer(
    publisher: PublisherClient,
    topic: str,
    response_target: str,
    user_id: str,
    interaction_type: str,
    event: dict[Any, Any],
    data: dict[Any, Any] = None,
):
    """
    Defer processing of a Slack message by publishing it to a Cloud PubSub topic.

    :param publisher: The GCP client publisher.
    :param topic: The topic name.
    :param response_target: The response target (URL or channel) for this Slack interaction.
    :param user_id: The Slack user ID.
    :param interaction_type: The interaction type (currently, "event" or "slash_command")
    :param event: Original event data to pass to the deferred processor
    :param data: Extra data you want to pass to the deferred processor (optional)
    :return: True if successful, False otherwise.
    """
    if data is None:
        data = {}

    try:
        publisher.publish(
            topic,
            json.dumps(
                {
                    "response_target": response_target,
                    "user_id": user_id,
                    "interaction_type": interaction_type,
                    "event": event,
                    "data": data,
                }
            ).encode("utf-8"),
            timeout=20,
        ).result(30)

        return True
    except TimeoutError | CancelledError | MessageTooLargeError:
        return False


def slack_deferred_slash_handler_gcp(
    base_func: Callable[[str, str, str, dict[str, Any], dict[str, Any]], None]
):
    """
    Decorator that can be applied to a Google cloud function to make the handling of deferred
    Slack messages (with slack_defer) more automatic. Just abstracts away some of the payload
    decoding and handling.

    Functions decorated by this should accept three string parameters - the response_url,
    user_id and text from the deferred message.

    To send messages back to Slack in this deferred flow, the slack_deferred_response
    function can be used (or you can just do a POST to the given response_url in your
    own code if you like full control).

    :param base_func: The function to decorate.
    :return: The decorated function. This is suitable for direct use as a GCP event triggered function.
    """

    def handler(event: dict[str, Any], *rest):
        try:
            (
                response_target,
                user_id,
                interaction_type,
                original_event,
                data,
            ) = __decode_payload(event)
            base_func(response_target, user_id, interaction_type, original_event, data)
        except KeyError:
            print("Received apparently-malformed message: " + str(event))

    return handler


def slack_deferred_response(response_url: str, content: dict[str, Any]) -> Response:
    """
    Post a response back to Slack for a deferred message.

    :param response_url: The Slack response URL from the original message.
    :param content: The message content (in Slack response format - see slack_messaging.py)
    :return: The result of the POST request (a Response object)
    """
    return requests.post(response_url, json=content)


def __decode_payload(
    event: dict[str, Any]
) -> tuple[str, str, str, dict[str, Any], dict[str, Any]]:
    data = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    return (
        data["response_target"],
        data["user_id"],
        data["interaction_type"],
        data["event"],
        data.get("data", {}),
    )
