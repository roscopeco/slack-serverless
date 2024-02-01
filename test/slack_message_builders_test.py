import sure
from slack_messaging import (
    slack_ephemeral_text_response,
    slack_ephemeral_blocks_response,
    slack_in_channel_text_response,
    slack_in_channel_blocks_response,
    slack_message_response,
    slack_tags,
)


def test_slack_ephemeral_text_response_happy():
    result = slack_ephemeral_text_response("hola")

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("text").which.should.equal("hola")


def test_slack_ephemeral_text_response_params_happy():
    result = slack_ephemeral_text_response("hola", params={"thread_ts": "12345678"})

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("text").which.should.equal("hola")
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_ephemeral_blocks_response_happy():
    result = slack_ephemeral_blocks_response([{"some": "block"}])

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("blocks").which.should.equal([{"some": "block"}])


def test_slack_ephemeral_blocks_response_two_blocks_happy():
    result = slack_ephemeral_blocks_response([{"some": "block"}, {"other": "block"}])

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("blocks").which.should.equal(
        [{"some": "block"}, {"other": "block"}]
    )


def test_slack_ephemeral_blocks_response_params_happy():
    result = slack_ephemeral_blocks_response(
        [{"some": "block"}], params={"thread_ts": "12345678"}
    )

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("blocks").which.should.equal([{"some": "block"}])
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_in_channel_text_response_happy():
    result = slack_in_channel_text_response("hola")

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("text").which.should.equal("hola")


def test_slack_in_channel_text_response_params_happy():
    result = slack_in_channel_text_response("hola", params={"thread_ts": "12345678"})

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("text").which.should.equal("hola")
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_in_channel_blocks_response_happy():
    result = slack_in_channel_blocks_response([{"some": "block"}])

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("blocks").which.should.equal([{"some": "block"}])


def test_slack_in_channel_blocks_response_two_blocks_happy():
    result = slack_in_channel_blocks_response([{"some": "block"}, {"other": "block"}])

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("blocks").which.should.equal(
        [{"some": "block"}, {"other": "block"}]
    )


def test_slack_in_channel_blocks_response_params_happy():
    result = slack_ephemeral_blocks_response(
        [{"some": "block"}], params={"thread_ts": "12345678"}
    )

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("blocks").which.should.equal([{"some": "block"}])
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_message_response_ephemeral_happy():
    result = slack_message_response("ephemeral", {"some": "content"})

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("some").which.should.equal("content")
    result.should_not.have.key("thread_ts")


def test_slack_message_response_params_ephemeral_happy():
    result = slack_message_response(
        "ephemeral", {"some": "content"}, params={"thread_ts": "12345678"}
    )

    result.should.have.key("response_type").which.should.equal("ephemeral")
    result.should.have.key("some").which.should.equal("content")
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_message_response_in_channel_happy():
    result = slack_message_response("in_channel", {"some": "content"})

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("some").which.should.equal("content")
    result.should_not.have.key("thread_ts")


def test_slack_message_response_params_in_channel_happy():
    result = slack_message_response(
        "in_channel", {"some": "content"}, params={"thread_ts": "12345678"}
    )

    result.should.have.key("response_type").which.should.equal("in_channel")
    result.should.have.key("some").which.should.equal("content")
    result.should.have.key("thread_ts").which.should.equal("12345678")


def test_slack_message_response_bad_type():
    slack_message_response.when.called_with(
        "BLAH", {"some": "content"}
    ).should.have.raised(ValueError)


def test_slack_tags_one_happy():
    slack_tags(user_ids=["1234"]).should.equal("<@1234>")


def test_slack_tags_two_happy():
    slack_tags(user_ids=["1234", "5678"]).should.equal("<@1234> <@5678>")


def test_slack_tags_none_empty():
    slack_tags(user_ids=None).should.be.empty
