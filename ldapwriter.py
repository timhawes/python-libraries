# -*- python -*-
#
# Tim Hawes <me@timhawes.com>
# 17th November 2008

import ldap
import ldap.modlist
from ldap.functions import explode_dn
import logging

class LDAPWriter(object):
    def __init__(self, conn, base, scope=ldap.SCOPE_ONELEVEL, dryrun=False, debug=False, ignore_attr_types=[]):
        self.conn   = conn
        self.base   = base
        self.scope  = scope
        self.dryrun = dryrun
        self.debug  = debug
        self.ignore_attr_types = ignore_attr_types
        self.seen = {}
        self.seen[str(explode_dn(base))] = True

    def put(self, dn, entry):
        status = None
        try:
            stored_object = self.conn.search_s(dn, ldap.SCOPE_BASE)[0]
            mods = ldap.modlist.modifyModlist(stored_object[1], entry, self.ignore_attr_types)
            if mods:
                if self.debug:
                    logging.info("update: %s" % (dn))
                    logging.info(mods)
                if not self.dryrun:
                    self.conn.modify_s(dn, mods)
                status = 'update'
            #else:
            #    #if self.debug:
            #    #    print "no-change: %s" % (dn)    
            #    status = 'nochange'
        except ldap.NO_SUCH_OBJECT:
            mods = ldap.modlist.addModlist(entry)
            if self.debug:
                logging.info("add: %s" % (dn))
            if not self.dryrun:
                self.conn.add_s(dn, mods)
            status = 'add'
        self.seen[str(explode_dn(dn))] = True
        return status
        
    def purge(self):
        delete = []
        for dn, entry in self.conn.search_s(self.base, self.scope, attrlist=[]):
            if not self.seen.has_key(str(explode_dn(dn))):
                delete.append(dn)
        delete.sort(lambda a, b: cmp(''.join(list(reversed(list(a)))), ''.join(list(reversed(list(b))))), reverse=True)
        for dn in delete:
            if self.debug:
                logging.info("delete: %s" % (dn))
            if not self.dryrun:
                self.conn.delete_s(dn)
        return delete
