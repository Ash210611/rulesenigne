# pylint: disable=C0209			# Don't require formatted strings.

import un_re.global_shared_variables as G

from un_re.indent import indent


# ===============================================================================
def get_ruleset_severities():
    """
    For now this is reading from a static table.
    """

    lst_filename = G.SCRIPT_DIR + '/un_re/resources/ruleset_severities.lst'

    G.RULESET_SEVERITIES = {}
    with open(lst_filename, 'r', encoding='utf-8') as lst_file:
        for line in lst_file.readlines():
            if line.find('#') > -1:
                continue

            (ruleset, rule_id, normal_severity, adjusted_severity) = line.split('|')

            ruleset = ruleset.strip()
            rule_id = rule_id.strip()
            normal_severity = normal_severity.strip()
            adjusted_severity = adjusted_severity.strip()

            # Convert all attributes to upper case
            ruleset = ruleset.upper()
            rule_id = rule_id.upper()
            normal_severity = normal_severity.upper()
            adjusted_severity = adjusted_severity.upper()

            key = '{0}|{1}|{2}'.format(
                ruleset,
                rule_id,
                normal_severity)

            if not key in G.RULESET_SEVERITIES:
                G.RULESET_SEVERITIES[key] = adjusted_severity

    # print (G.RULESET_SEVERITIES)

    if G.VERBOSE:
        if len(G.RULESET_SEVERITIES) == 1:
            indent('Read {0:5,d} ruleset severity.'.format(
                len(G.RULESET_SEVERITIES)))
        else:
            indent('Read {0:5,d} ruleset severities.'.format(
                len(G.RULESET_SEVERITIES)))
