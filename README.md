[![Stories in Ready](https://badge.waffle.io/TranscribersOfReddit/ToR_OCR.png?label=ready&title=Ready)](http://waffle.io/TranscribersOfReddit/ToR_OCR)

# Flair Moderator Bot - Transcribers Of Reddit

This is the source code for the ToR Flair Moderator Helper (`/u/tor_flair_bot`). It forms one part of the team that assists in the running of /r/TranscribersOfReddit (ToR), which is privileged to have the incredibly important job of organizing crowd-sourced transcriptions of images, video, and audio.

As a whole, the ToR bots are designed to be as light on local resources as they can be, though there are some external requirements.

- Redis (tracking completed posts and queue system)

> **NOTE:**
>
> This code is not complete. The praw.ini file is required to run the bots and
> contains information such as the useragents and certain secrets. It is built
> for Python 3.6.

## Installation

```
$ git clone https://github.com/GrafeasGroup/tor_flair.git tor-flair
$ pip install --process-dependency-links tor-flair/
```

OR

```
$ pip install --process-dependency-links 'git+https://github.com/GrafeasGroup/tor_flair.git@master#egg=tor_flair'
```

## High-level functionality

Monitoring daemon (via Redis queue):

- Pull job (by post id) off of queue:
  - Get username and subreddit from job
  - If it is a moderator of that subreddit:
    - get config wiki page
    - set flair text and css class for user

### Running Flair Moderator Bot

```
$ tor-flair
# => [daemon mode + logging]
```

## Contributing

See [`CONTRIBUTING.md`](/CONTRIBUTING.md) for more.
