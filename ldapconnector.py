# -*- python -*-
#
# Tim Hawes <me@timhawes.com>
# 13th June 2007

import ldap
import os
import pwd
import re

def ldap_config_parser():
    filenames = ["/etc/openldap/ldap.conf",
                 "/etc/ldap/ldap.conf",
		 "/etc/ldap.conf"]
    try:
        home = pwd.getpwuid(os.getuid())[5]
        filenames.append(os.path.join(home, "ldaprc"))
        filenames.append(os.path.join(home, ".ldaprc"))
    except:
        pass
    filenames.append("ldaprc")
    line_re = re.compile(u'^([\w\_]+)\s+(.+)(\#.+)?\r?\n?$')
    config = {}
    for filename in filenames:
	try:
	    for line in open(filename, "r"):
		m = line_re.match(line)
		if m:
		    config[m.group(1).lower()] = m.group(2)
	except:
	    pass
    return config

def SmartLDAPObject(debug=False):
    config = ldap_config_parser()
    if debug:
	print "Loaded config: %r" % (config)
    kwargs = {}
    if config.has_key("binddn"):
	kwargs["who"] = config["binddn"]
    if config.has_key("bindpw"):
	kwargs["cred"] = config["bindpw"]
    if config.has_key("uri"):
	if debug:
	    print "Creating SmartLDAPObject with parameters: %r, %r" % (config["uri"], kwargs)
	return ldap.ldapobject.SmartLDAPObject(config["uri"], **kwargs)

if __name__ == "__main__":
    ldap_object = SmartLDAPObject(debug=True)
    print ldap_object.whoami_s()

