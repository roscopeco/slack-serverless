import json
from typing import Callable, Any

import requests
from requests import Response

from botocore.exceptions import ClientError


def slack_defer_aws(
    publisher: Any,  # TODO fix this type hint
    topic_arn: str,
    response_target: str,
    user_id: str,
    interaction_type: str,
    event: dict[Any, Any],
    data: dict[Any, Any] = None,
):
    """
    Defer processing of a Slack message by publishing it to an SNS topic.

    :param publisher: The SNS client publisher.
    :param topic_arn: The topic arn
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
            TopicArn=topic_arn,
            MessageGroupId="slack_deferred",
            MessageDeduplicationId=event["event_id"],
            Message=json.dumps(
                {
                    "response_target": response_target,
                    "user_id": user_id,
                    "interaction_type": interaction_type,
                    "event": event,
                    "data": data,
                }
            ),
        )

        return True
    except ClientError as e:
        print(e)
        return False


def slack_deferred_slash_handler_aws(
    base_func: Callable[[str, str, str, dict[str, Any], dict[str, Any]], None]
):
    """
    Decorator that can be applied to an AWS Lambda function to make the handling of deferred
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

    def handler(event: dict[str, Any], *rest, **kwargs):
        try:
            (
                response_target,
                user_id,
                interaction_type,
                original_event,
                data,
            ) = __decode_payload(event)
            base_func(
                response_target,
                user_id,
                interaction_type,
                original_event,
                data,
                *rest,
                **kwargs,
            )
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
    body = json.loads(event["Records"][0]["body"])
    data = json.loads(body["Message"])
    return (
        data["response_target"],
        data["user_id"],
        data["interaction_type"],
        data["event"],
        data.get("data", {}),
    )
