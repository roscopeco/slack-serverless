import httpretty
import sure
from slack_messaging import (
    slack_post_text_message,
    slack_post_blocks_message,
    slack_post_message,
)


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_message_happy():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            message={"text": "test message"},
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "text": "test message"}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_message_happy_with_params():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            message={"text": "test message", "thread_ts": "12345678"},
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "text": "test message", "thread_ts": "12345678"}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_message_bad_request():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=400)

    assert (
        slack_post_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            message={"text": "test message"},
        )
        is False
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_message_401():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=401)

    assert (
        slack_post_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            message={"text": "test message"},
        )
        is False
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_text_message_happy():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_text_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            text="test message",
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "text": "test message"}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_text_message_happy_with_params():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_text_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            text="test message",
            params={"thread_ts": "12345678"},
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "text": "test message", "thread_ts": "12345678"}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_text_message_bad_request():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=400)

    assert (
        slack_post_text_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            text="simple message",
        )
        is False
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_text_message_401():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=401)

    assert (
        slack_post_text_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            text="simple message",
        )
        is False
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_blocks_message_happy():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_blocks_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            blocks={"one": "two"},
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "blocks": {"one": "two"}}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_blocks_message_happy_with_params():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=200)

    assert (
        slack_post_blocks_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            blocks={"one": "two"},
            params={"thread_ts": "12345678"},
        )
        is True
    )

    httpretty.last_request().headers.should.have.key(
        "Authorization"
    ).which.should.equal("Bearer test-token")
    httpretty.last_request().body.should.equal(
        b'{"channel": "test-channel", "blocks": {"one": "two"}, "thread_ts": "12345678"}'
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_blocks_message_bad_request():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=400)

    assert (
        slack_post_blocks_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            blocks={"one": "two"},
        )
        is False
    )


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_slack_post_blocks_message_401():
    httpretty.register_uri(httpretty.POST, "https://test.slack.endpoint/", status=401)

    assert (
        slack_post_blocks_message(
            endpoint="https://test.slack.endpoint/",
            slack_access_token="test-token",
            channel="test-channel",
            blocks={"one": "two"},
        )
        is False
    )
