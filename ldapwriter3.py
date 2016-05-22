# -*- python -*-
#
# Tim Hawes <me@timhawes.com>
# 17th November 2008
# 23rd May 2016 - modified for ldap3 library

import logging
from ldap3 import BASE, LEVEL, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from ldap3.utils.dn import safe_dn, to_dn

def modlist(old, new, ignore_attr_types=[]):
    mods = {}
    seen_attr = {}
    for attr in old.keys():
        seen_attr[attr] = True
        if attr in ignore_attr_types:
            continue
        if attr in new:
            if old[attr] == new[attr]:
                # no change
                pass
            else:
                # modify
                mods[attr] = [(MODIFY_REPLACE, new[attr])]
        else:
            # delete
            mods[attr] = [(MODIFY_DELETE, [])]
    for attr in new.keys():
        if attr in ignore_attr_types:
            continue
        if attr in old:
            pass
        else:
            # add
            mods[attr] = [(MODIFY_ADD, new[attr])]
    return mods

def addmodlist(new, ignore_attr_types=[]):
    mods = {}
    for attr in new.keys():
        if attr in ignore_attr_types:
            continue
        mods[attr] = [(MODIFY_ADD, new[attr])]
    return mods

def rev_dn(dn):
    return ','.join(reversed(to_dn(dn)))

class LDAPWriter(object):
    def __init__(self, conn, base, scope=LEVEL, dryrun=False, debug=False, ignore_attr_types=[]):
        self.conn   = conn
        self.base   = base
        self.scope  = scope
        self.dryrun = dryrun
        self.debug  = debug
        self.ignore_attr_types = ignore_attr_types
        self.seen = {}
        self.seen[safe_dn(base)] = True

    def put(self, dn, entry):
        status = None
        self.conn.search(search_base=dn, search_filter="(objectClass=*)", search_scope=BASE, attributes="*")
        if len(self.conn.response) == 1:
            stored_object = self.conn.response[0]
            mods = modlist(stored_object["attributes"], entry, self.ignore_attr_types)
            if mods:
                if self.debug:
                    logging.info("update: %s" % (dn))
                    logging.info(mods)
                if not self.dryrun:
                    self.conn.modify(dn, mods)
                    pass
                status = 'update'
            else:
                if self.debug:
                    logging.info("no-change: %s" % (dn))
                status = 'nochange'
        else:
            if self.debug:
                logging.info("add: %s" % (dn))
            entry2 = {}
            for k, v in entry.items():
                if k not in self.ignore_attr_types:
                    entry2[k] = v
            if not self.dryrun:
                self.conn.add(dn, attributes=entry2)
            status = 'add'
        self.seen[safe_dn(dn)] = True
        return status

    def purge(self):
        delete = []
        results = self.conn.extend.standard.paged_search(self.base, "(objectClass=*)", self.scope, attributes=[])
        for entry in results:
            dn = entry["dn"]
            if safe_dn(dn) not in self.seen:
                delete.append(dn)
        delete.sort(key=rev_dn, reverse=True)
        for dn in delete:
            if self.debug:
                logging.info("delete: %s" % (dn))
            if not self.dryrun:
                self.conn.delete(dn)
        return delete
