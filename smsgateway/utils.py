import re

def strspn(source, allowed):
    newchrs = []
    for c in source:
        if c in allowed:
            newchrs.append(c)
    return u''.join(newchrs)

def firstmatch(source, regexes):
    for regex in regexes:
        match = re.match(regex, source)
        if match is not None:
            return match.groups()[0]
    return None

def check_cell_phone_number(number):
    cleaned_number = strspn(number, u'+0123456789')

    if not u'+' in cleaned_number[:1]:
        cleaned_number = u'+%s' % cleaned_number

    return cleaned_number

#    cleaned_number = firstmatch(cleaned_number, [r'^04(\d{8})$', r'^324(\d{8})$', r'^\+324(\d{8})$', r'^\+3204(\d{8})$', r'^4(\d{8})$', r'^00324(\d{8})$'])
#
#    if cleaned_number is None:
#        return None
#
#    return u'+324%s' % cleaned_number

def truncate_sms(text, max_length=160):
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length-3] + '...'

def parse_sms(content):
    content = content.upper().strip()
    from smsgateway.backends.base import hook
    for keyword, subkeywords in hook.iteritems():
        if content[:len(keyword)] == unicode(keyword):
            remainder = content[len(keyword):].strip()
            if '*' in subkeywords:
                parts = remainder.split(u' ')
                subkeyword = parts[0].strip()
                if subkeyword in subkeywords:
                    return [keyword] + parts
                return keyword, remainder
            else:
                for subkeyword in subkeywords:
                    if remainder[:len(subkeyword)] == unicode(subkeyword):
                        subremainder = remainder[len(subkeyword):].strip()
                        return [keyword, subkeyword] + subremainder.split()
    return None
