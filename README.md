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
