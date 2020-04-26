from api.news_headlines import *
from api.news_headlines import params


logger = logging.getLogger('app')
def twitter_processing():
    # create instance of the tweepy tweet stream listener
    tweetlistener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)

    # create instance of the tweepy stream
    stream = Stream(auth, tweetlistener)
    # grab any twitter users from links in web page at url
    if params['url']:
        twitter_users = get_twitter_users_from_url(params['url'])
        if len(twitter_users) > 0:
            twitter_feeds = twitter_users
        else:
            logger.info("No twitter users found in links on web page, exiting")
            sys.exit(1)

    # grab twitter users from file
    if params['file']:
        twitter_users = get_twitter_users_from_file(params['file'])
        if len(twitter_users) > 0:
            useridlist = twitter_users
        else:
            logger.info("No twitter users found in file, exiting")
            sys.exit(1)
    elif params['keywords'] is None:
        # build user id list from user names
        logger.info("Looking up Twitter user ids from usernames... (use -f twitteruserids.txt for cached user ids)")
        useridlist = []
        while True:
            for u in twitter_feeds:
                try:
                    # get user id from screen name using twitter api
                    user = api.get_user(screen_name=u)
                    uid = str(user.id)
                    if uid not in useridlist:
                        useridlist.append(uid)
                    time.sleep(randrange(2, 5))
                except TweepError as te:
                    # sleep a bit in case twitter suspends us
                    logger.warning("Tweepy exception: twitter api error caused by: %s" % te)
                    logger.info("Sleeping for a random amount of time and retrying...")
                    time.sleep(randrange(2, 30))
                    continue
                except KeyboardInterrupt:
                    logger.info("Ctrl-c keyboard interrupt, exiting...")
                    stream.disconnect()
                    sys.exit(0)
            break

        if len(useridlist) > 0:
            logger.info('Writing twitter user ids to text file %s' % twitter_users_file)
            try:
                f = open(twitter_users_file, "wt", encoding='utf-8')
                for i in useridlist:
                    line = str(i) + "\n"
                    if type(line) is bytes:
                        line = line.decode('utf-8')
                    f.write(line)
                f.close()
            except (IOError, OSError) as e:
                logger.warning("Exception: error writing to file caused by: %s" % e)
                pass
            except Exception as e:
                raise

    try:
        # search twitter for keywords
        logger.info('Stock symbol: ' + str(params['symbol']))
        logger.info('NLTK tokens required: ' + str(nltk_tokens_required))
        logger.info('NLTK tokens ignored: ' + str(nltk_tokens_ignored))
        logger.info('Listening for Tweets (ctrl-c to exit)...')
        if params['keywords'] is None:
            logger.info('No keywords entered, following Twitter users...')
            logger.info('Twitter Feeds: ' + str(twitter_feeds))
            logger.info('Twitter User Ids: ' + str(useridlist))
            stream.filter(follow=useridlist, languages=['en'])
        else:
            # keywords to search on twitter
            # add keywords to list
            keywords = params['keywords'].split(',')
            if params['addtokens']:
                # add tokens to keywords to list
                for f in nltk_tokens_required:
                    keywords.append(f)
            logger.info('Searching Twitter for keywords...')
            logger.info('Twitter keywords: ' + str(keywords))
            stream.filter(track=keywords, languages=['en'])
    except TweepError as te:
        logger.debug("Tweepy Exception: Failed to get tweets caused by: %s" % te)
    except KeyboardInterrupt:
        print("Ctrl-c keyboard interrupt, exiting...")
        stream.disconnect()
        sys.exit(0)
if __name__ == '__main__':
    twitter_processing();
