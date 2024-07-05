## Utility library for serverless Slack apps

![PyPI](https://img.shields.io/pypi/v/slack-serverless)

This is a (currently very simple) library that eases development of serverless Slack
app and bots.

Currently, it targets Google Cloud Platform (but is easily generalised), and provides 
a decorator and some utility functions that make Slack signature verification automatic
and help with building responses in a very lightweight fashion.

I will grow it with things I end up needing in my work, but if you have different
needs and want to extend the library to support them, then PRs would be gratefully
received!

### MVP Example

This will accept any slash command you've configured for your bot, and just greet 
the user who calls it, tagging them in the reply. 

```python
from slack_serverless import slack_slash_command_gcp
from slack_messaging import slack_in_channel_text_response, slack_tags

@slack_slash_command_gcp(slack_signing_key=YOUR_SIGNING_KEY)
def command_handler(payload):
    return slack_in_channel_text_response(f"Hi there <@{slack_tags([payload['user_id']])}>")
```

### Message Deferral

> **Note** to avoid dependency conflicts, this library does not depend on the
> cloud provider APIs that are needed. For GCP, be sure to add `google-cloud-pubsub>=2.18.1`
> to your `requirements.txt` (or whatever) if you're using deferral.

If you need to take more than three seconds to reply to a Slack message, the usual
thing to do in a serverless environment is hand off the message to another function,
and have the first one acknowledge receipt back to Slack within three seconds. This 
is required - failing to respond in a timely fashion will result in the user seeing
an error message.

This library provides a comfort wrapper around this use case - all you need to do is
set up a PubSub topic (or your cloud's equivalent, though only GCP is supported as yet)
and defer the message in your main Slack handler with the `slack_defer` function.

You then have a second lambda, triggered by the pubsub (Eventarc or equivalent) in 
which the main function is decorated with `@slack_deferred_slash_handler_gcp`
(despite the name, it supports both events and slash commands - it'll be 
changing soon) and handles the event.

This will take care of wrapping and unwrapping the event appropriately and generally
trades of some ease of use for a little flexibility. If it doesn't meet your needs
you can of course just ignore it and code up the functionality yourself.


### Other Cloud Providers

Things will be a bit more manual here (but I'll happily add comfort wrappers if
there's enough call and a PR that contributes them 😉).

The easiest thing to do is use the `slack_slash_command` decorator, which 
is similar to the `gcp` one above but needs you pass in a couple of `Callable`s
the code will use to get access to the data in a provider-specific way.

Take a look at the code in `slack_serverless.py` for examples to get you started.

### Developing

Don't forget to set up `pre-commit` if you're developing things, especially if you
plan to push a PR.

### Legal Mumbo-Jumbo

Copyright (c)2023 Ross Bamford (and contributors)

License: MIT (see `LICENSE.md` for details).
