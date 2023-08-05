import hashlib
import hmac
import time

from urllib.parse import parse_qs
from typing import Any, Callable


def slack_slash_command_gcp(slack_signing_secret: str):
    """
    Decorate a function as a GCP Cloud Function-compatible Slack Webhook. This decorator will automatically
    handle Slack signature verification for you and will pass the decoded payload into your decorated function.

    The decorated function should accept a single request argument compatible with dict[str, list[str]],
    which will hold the extracted Slack payload.

    The return value should be a dict[str, str] with the JSON body for the response back to Slack.

    :param slack_signing_secret: The Slack signing secret for your app.
    :return: The decorated function. This can be used directly as a GCP function handler.
    """
    return slack_slash_command(
        slack_signing_secret,
        lambda request, name: request.headers.get(name),
        lambda request: request.get_data(),
        lambda raw_body: parse_qs(raw_body.decode("utf8")),
        lambda body, status: (body, status, __json_header()),
    )


def slack_slash_command(
    slack_signing_secret: str,
    header_func: Callable[[Any, str], str],
    raw_body_func: Callable[[Any], bytes],
    parse_body_func: Callable[[bytes], dict[str, list[str]]],
    response_func: Callable[
        [dict[str, Any], int], tuple[dict[str, Any], int, dict[str, str]]
    ],
):
    """
    Decorate a function as a generic serverless Slack Webhook handler. This decorator will automatically
    handle Slack signature verification for you and will pass the decoded payload into your decorated function.

    You must provide a number of callables that interface the decorator with your provider-specific
    request/response objects. See the GCP implementation above for an example.

    :param slack_signing_secret: The Slack signing secret for your app.
    :param header_func: A function that obtains a named header from your cloud's request object.
    :param raw_body_func: A function that obtains the raw body from your cloud's request object.
    :param parse_body_func: A function that parses the raw body from your cloud's request object as form-encoded data
    :param response_func: A function that encodes a JSON body and HTTP status code as a response for your cloud.
    :return: The decorated function. This can be used directly as a function handler for your cloud platform.
    """

    def decorator(base_func: Callable[[dict[str, list[str]]], dict[str, Any]]):
        def handler(request: Any) -> tuple[dict[str, Any], int, dict[str, str]]:
            timestamp = header_func(request, "X-Slack-Request-Timestamp")
            sig = header_func(request, "X-Slack-Signature")
            request_data = raw_body_func(request)

            if timestamp is None or sig is None:
                return response_func(__unauthorized(), 401)

            if abs(time.time() - int(timestamp)) > 300:
                return response_func(__unauthorized(), 401)

            basestring = "v0:" + str(timestamp) + ":" + str(request_data.decode())
            expected_signature = (
                "v0="
                + hmac.new(
                    slack_signing_secret.encode(),
                    msg=basestring.encode(),
                    digestmod=hashlib.sha256,
                ).hexdigest()
            )

            if not hmac.compare_digest(expected_signature, sig):
                return response_func(__unauthorized(), 401)

            return response_func(base_func(parse_body_func(request_data)), 200)

        return handler

    return decorator


def __unauthorized() -> dict[str, str]:
    return {"message": "nope"}


def __json_header() -> dict[str, str]:
    return {"Content-Type": "application/json"}
