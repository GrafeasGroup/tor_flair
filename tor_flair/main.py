import logging
import time

from tor_core.config import config
from tor_core.helpers import get_wiki_page
from tor_core.helpers import run_until_dead
from tor_core.initialize import build_bot

from tor_flair import __version__

instructions_page = (
    'Thanks for using the Transcribers of Reddit flair helper bot! Our goal '
    'is to make your day a little easier by automating the process of identifying '
    'our volunteers on your subreddit.\n\n'
    'Simply set flair-text and / or flair-css in /wiki/config/tor-flair/settings '
    'and u/tor_flair_bot will get the changes the next time a volunteer accepts a '
    'job for your subreddit.\n\n'
    'If you have any questions or issues with the bot, please '
    'send a modmail to r/TranscribersOfReddit and we\'ll get you sorted as quickly '
    'as we can!'
)


settings_page = (
    '; Set the flair text and css class below to whatever you want.  \n'
    '; Both options are optional - whichever one is blank be left alone.  \n'
    '; Example:  \n'
    ';  \n'
    '; flair-text: darn cool person  \n'
    '; flair-css: coolperson  \n'
    '\n\n'
    'flair-text:\n\n'
    'flair-css:'
)

settings_location = 'tor-flair/config/settings'
instructions_location = 'tor-flair/config/instructions'


def setup_wiki(subreddit):
    subreddit.wiki.create(settings_location, content=settings_page)
    subreddit.wiki.create(instructions_location, content=instructions_page)


def get_config(subreddit):
    return get_wiki_page(settings_location, config, subreddit=subreddit)


def check_inbox(config):
    logging.debug('Checking inbox...')
    for item in config.r.inbox.unread():
        if 'invitation to moderate' in item.subject.lower():
            logging.info(
                'Received offer to moderate {}!'.format(item.subreddit.display_name)
            )
            item.subreddit.mod.accept_invite()
            setup_wiki(item.subreddit)
            config.redis.sadd('flair_subreddits', item.subreddit.display_name)
            item.mark_read()
        if 'has been removed as a moderator from' in item.subject.lower():
            logging.warning(
                'I\'ve been kicked from {}!'.format(item.subreddit.display_name)
            )
            config.redis.srem('flair_subreddits', item.subreddit.display_name)
            item.mark_read()


def run(config):
    check_inbox(config)
    new_job = config.redis.lpop('flair_queue')
    if not new_job:
        time.sleep(10)
        return
    # format: user::subreddit
    new_job = new_job.decode()  # bytes to str
    user = config.r.redditor(
        new_job[:new_job.index('::')]
    )
    subreddit = config.r.subreddit(new_job[new_job.index('::')+2:])

    logging.info(
        'Setting flair for {} in {}...'.format(user.name, subreddit.display_name)
    )

    subreddit_config = get_config(subreddit).split('\r\n')
    subreddit_config = [y for y in subreddit_config if not y.startswith(';') and y != '']

    text = subreddit_config[0][11:].strip()
    css = subreddit_config[1][10:].strip()

    if text == '':
        # get the existing flair so we can write it back
        # Also, PRAW, why is this a generator for one user?
        text = [x for x in subreddit.flair(redditor=user)][0]['flair_text']
    if css == '':
        css = [x for x in subreddit.flair(redditor=user)][0]['flair_css_class']

    subreddit.flair.set(user, text=text, css_class=css)
    logging.info('Flair set!')


def main():
    """
        Console scripts entry point for ToR_Flair Bot
    """

    build_bot('bot_flair',
              __version__,
              full_name='u/tor_flair_bot',
              log_name='flair.log')
    run_until_dead(run)

if __name__ == '__main__':
    main()
