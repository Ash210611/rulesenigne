# pylint: disable=C0209			# Don't require formatted strings.

import re

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.indent import indent


# ===============================================================================
def get_rules_urls():
    rules_urls_filename = G.SCRIPT_DIR + C.Rule.rules_urls_filename

    num_urls = 0

    with open(rules_urls_filename, 'r', encoding='utf-8') as url_file:
        for line in url_file.readlines():
            if re.search('^#', line):
                continue

            line = line.strip()
            rule_id, url = line.split(r'|')

            rule_id = rule_id.strip()
            url = url.strip()

            # print (__file__)
            # print (f'rule_id: {rule_id}')
            # print (f'url:     {url}')
            # print (f'len(url): {len(url)}')
            if rule_id in G.SHOULD_CHECK_RULE and \
                    len(url) > 0:
                G.RULES[rule_id].url = url
                num_urls += 1

    if G.VERBOSE:
        indent('Read {0:5,d} documentation URLs.'.format(num_urls))
