import hashlib
import hmac
import json
import time
import base64

from urllib.parse import parse_qs
from typing import Any, Callable


def slack_slash_command_gcp(slack_signing_secret: str):
    """
    Decorate a function as a GCP Cloud Function-compatible Slack slash command webhook handler.

    This decorator will automatically handle Slack signature verification for you and will
    pass the decoded payload into your decorated function.

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


def slack_slash_command_aws_api_gateway_proxy(slack_signing_secret: str):
    """
    Decorate a function as an AWS API Gateway lambda proxy compatible Slack slash command webhook handler.

    This decorator will automatically handle Slack signature verification for you and will
    pass the decoded payload into your decorated function.

    The decorated function should accept a single request argument compatible with dict[str, list[str]],
    which will hold the extracted Slack payload.

    The return value should be a dict[str, str] with the JSON body for the response back to Slack.

    :param slack_signing_secret: The Slack signing secret for your app.
    :return: The decorated function. This can be used directly as an AWS lambda function handler.
    """
    return slack_slash_command(
        slack_signing_secret,
        lambda request, name: request["headers"].get(name),
        lambda request: base64.b64decode(request["body"]),
        lambda raw_body: parse_qs(raw_body.decode()),
        lambda body, status: {
            "statusCode": status,
            "body": body,
            "headers": __json_header(),
        },
    )


def slack_slash_command(
    slack_signing_secret: str,
    header_func: Callable[[Any, str], str],
    raw_body_func: Callable[[Any], bytes],
    parse_body_func: Callable[[bytes], dict[str, list[str]]],
    response_func: Callable[[dict[str, Any], int], Any],
):
    """
    Decorate a function as a generic serverless Slack slash command webhook handler.

    This decorator will automatically handle Slack signature verification for you and will
    pass the decoded payload into your decorated function.

    You must provide a number of callables that interface the decorator with your provider-specific
    request/response objects. See the GCP implementation above for an example.

    :param slack_signing_secret: The Slack signing secret for your app.
    :param header_func: A function that obtains a named header from your cloud's request object.
    :param raw_body_func: A function that obtains the raw body from your cloud's request object.
    :param parse_body_func: A function that parses the raw body of your cloud's request object as form-encoded data
    :param response_func: A function that encodes a JSON body and HTTP status code as a response for your cloud.
    :return: The decorated function. This can be used directly as a function handler for your cloud platform.
    """

    def decorator(base_func: Callable[[dict[str, list[str]]], dict[str, Any]]):
        def handler(
            request: Any, *args, **kwargs
        ) -> tuple[dict[str, Any], int, dict[str, str]]:
            timestamp, sig, request_data = __extract_validation_data(
                request, header_func, raw_body_func
            )

            if not is_valid_slack_request(
                slack_signing_secret, timestamp, sig, request_data
            ):
                return response_func(__unauthorized(), 401)

            return response_func(
                base_func(parse_body_func(request_data), *args, **kwargs), 200
            )

        return handler

    return decorator


def slack_event_webhook_gcp(slack_signing_secret: str):
    """
    Decorate a function as a GCP Cloud Function-compatible Slack Event API webhook handler.

    This decorator will automatically handle Slack signature verification and the API registration
    challenge for you and will pass the decoded payload (JSON) into your decorated function.

    The decorated function should accept a single request argument compatible with dict[str, list[str]],
    which will hold the extracted Slack payload.

    The return value should be a dict[str, str] with the JSON body for the response back to Slack.

    :param slack_signing_secret: The Slack signing secret for your app.
    :return: The decorated function. This can be used directly as a GCP function handler.
    """
    return slack_event_webhook(
        slack_signing_secret,
        lambda request, name: request.headers.get(name),
        lambda request: request.get_data(),
        lambda raw_body: json.loads(raw_body.decode("utf8")),
        lambda body, status: (body, status, __json_header()),
    )


def slack_event_webhook_aws_api_gateway_proxy(slack_signing_secret: str):
    """
    Decorate a function as an AWS API Gateway lambda proxy compatible Slack Event API webhook handler.

    This decorator will automatically handle Slack signature verification and the API registration
    challenge for you and will pass the decoded payload (JSON) into your decorated function.

    The decorated function should accept a single request argument compatible with dict[str, list[str]],
    which will hold the extracted Slack payload.

    The return value should be a dict[str, str] with the JSON body for the response back to Slack.

    :param slack_signing_secret: The Slack signing secret for your app.
    :return: The decorated function. This can be used directly as a Lambda function handler.
    """
    return slack_event_webhook(
        slack_signing_secret,
        lambda request, name: request["headers"].get(name),
        lambda request: request["body"],
        lambda raw_body: json.loads(raw_body),
        lambda body, status: {
            "statusCode": status,
            "body": json.dumps(body),
            "headers": __json_header(),
        },
    )


def slack_event_webhook(
    slack_signing_secret: str,
    header_func: Callable[[Any, str], str],
    raw_body_func: Callable[[Any], bytes],
    parse_body_func: Callable[[bytes], dict[str, Any]],
    response_func: Callable[[dict[str, Any], int], Any],
):
    """
    Decorate a function as a generic serverless Slack Event API webhook handler.

    This decorator will automatically handle Slack signature verification and the API registration
    challenge for you and will pass the decoded payload (JSON) into your decorated function.

    You must provide a number of callables that interface the decorator with your provider-specific
    request/response objects. See the GCP implementation above for an example.

    :param slack_signing_secret: The Slack signing secret for your app.
    :param header_func: A function that obtains a named header from your cloud's request object.
    :param raw_body_func: A function that obtains the raw body from your cloud's request object.
    :param parse_body_func: A function that parses the raw body of your cloud's request object as JSON
    :param response_func: A function that encodes a JSON body and HTTP status code as a response for your cloud.
    :return: The decorated function. This can be used directly as a function handler for your cloud platform.
    """

    def decorator(base_func: Callable[[dict[str, Any]], dict[str, Any]]):
        def handler(
            request: Any, *args, **kwargs
        ) -> tuple[dict[str, Any], int, dict[str, str]]:
            timestamp, sig, request_data = __extract_validation_data(
                request, header_func, raw_body_func
            )

            if not is_valid_slack_request(
                slack_signing_secret, timestamp, sig, request_data
            ):
                return response_func(__unauthorized(), 401)

            body = parse_body_func(request_data)

            if body.get("type") == "url_verification":
                return response_func({"challenge": body["challenge"]}, 200)

            return response_func(base_func(body, *args, **kwargs), 200)

        return handler

    return decorator


def __extract_validation_data(
    request: Any,
    header_func: Callable[[Any, str], str],
    raw_body_func: Callable[[Any], bytes],
) -> tuple[str, str, bytes]:
    timestamp = header_func(request, "X-Slack-Request-Timestamp")
    sig = header_func(request, "X-Slack-Signature")
    request_data = raw_body_func(request)

    return timestamp, sig, request_data


def is_valid_slack_request(
    slack_signing_secret: str,
    timestamp: str,
    signature: str,
    raw_body: bytes,
) -> bool:
    """
    Determine whether the given Slack signing secret will validate the given
    request data.

    :param slack_signing_secret: The Slack signing secret (from your App).
    :param timestamp: The value from the X-Slack-Request-Timestamp header.
    :param signature: The value from the X-Slack-Signature header.
    :param raw_body: The raw (bytes) payload.
    :return: True if validation is successful, False otherwise.
    """
    if timestamp is None or signature is None:
        return False

    if abs(time.time() - int(timestamp)) > 300:
        return False

    if isinstance(raw_body, bytes):
        raw_body = str(raw_body.decode())

    basestring = "v0:" + str(timestamp) + ":" + raw_body
    expected_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret.encode(),
            msg=basestring.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(expected_signature, signature):
        return False

    return True


def __unauthorized() -> dict[str, str]:
    return {"message": "nope"}


def __json_header() -> dict[str, str]:
    return {"Content-Type": "application/json"}
