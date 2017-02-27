from logging import getLogger
from phonenumbers import parse, format_number, PhoneNumberFormat
from re import sub

from django.conf import settings

logger = getLogger(__name__)


def strspn(source, allowed):
    newchrs = []
    for c in source:
        if c in allowed:
            newchrs.append(c)
    return u''.join(newchrs)


def check_cell_phone_number(number):
    parsed_number = parse(number, getattr(settings, 'SMSGATEWAY_DEFAULT_LOCALE', 'BE'))
    return format_number(parsed_number, PhoneNumberFormat.E164)


def truncate_sms(text, max_length=160):
    text = text.strip()
    if len(text) <= max_length:
        return text
    else:
        logger.error('Trying to send an SMS that is too long: %s', text)
        return text[:max_length-3] + '...'


def _match_keywords(content, hooks):
    """
    Helper function for matching a message to the hooks. Called recursively.

    :param str content: the (remaining) content to parse
    :param dict hooks: the hooks to try
    :returns str: the message without the keywords
    """
    # Go throught the different hooks
    matched = False
    for keyword, hook in hooks.iteritems():
        # If the keyword of this hook matches
        if content.startswith(keyword + ' ') or keyword == content:
            matched = True
            break

    # If nothing matched, see if there is a wildcard
    if not matched and '*' in hooks:
        return content

    # Split off the keyword
    remaining_content = content.split(' ', 1)[1] if ' ' in content else ''

    # There are multiple subkeywords, recurse
    if isinstance(hook, dict):
        return _match_keywords(remaining_content, hook)
    # This is the callable, we're done
    else:
        return remaining_content


def parse_sms(content):
    """
    Parse an sms message according to the hooks defined in the settings.

    :param str content: the message to parse
    :returns list: the message without keywords, split into words
    """
    # work with uppercase and single spaces
    content = content.upper().strip()
    content = sub('\s+', ' ', content)

    from smsgateway.backends.base import all_hooks
    content = _match_keywords(content, all_hooks)
    return content.split(' ')
