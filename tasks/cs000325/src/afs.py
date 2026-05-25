#! /usr/bin/env python

from __future__ import print_function
import random
from optparse import OptionParser
import string


# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return


def tprint(str):
    print(str)


def dprint(str):
    return


def dospace(howmuch):
    for i in range(howmuch + 1):
        print("%28s" % " ", end="")


# given list, pick random element and return it
def pickrand(tlist):
    n = int(random.random() * len(tlist))
    p = tlist[n]
    return p


# given number, conclude if nth bit is set
def isset(num, index):
    mask = 1 << index
    return (num & mask) > 0


# useful instead of assert
def zassert(cond, str):
    if cond == False:
        print("ABORT::", str)
        exit(1)


#
# Which files are used in the simulation
#
# Not representing a realistic piece of anything
# but rather just for convenience when generating
# random traces ...
#
# Files are named 'a', 'b', etc. for ease of use
# Could probably add a numeric aspect to allow
# for more than 26 files but who cares
#


class files:
    def __init__(self, numfiles):
        pass

    def getfiles(self):
        pass

    def getvalue(self):
        pass


#
# Models the actions of the AFS server
#
# The only real interactions are get/put
# get() causes the server to track which files cache what;
# put() may cause callbacks to invalidate client caches
#
class server:
    def __init__(self, files, solve, detail):
        pass

    def stats(self):
        pass

    def filestats(self, printcontents):
        pass

    def setclients(self, clients):
        pass

    def get(self, client, fname):
        pass

    def put(self, client, fname, value):
        pass


#
# Per-client file descriptors
#
# Would be useful if the simulation allowed more
# than one active file open() at a time; it kind
# of does but this isn't really utilized
#
class filedesc:
    def __init__(self, max=1024):
        pass

    def alloc(self, fname, sfd=-1):
        pass

    def lookup(self, sfd):
        pass

    def free(self, sfd):
        pass


#
# The client cache
#
# Just models what files are cached.
# When a file is opened, its contents are fetched
# from the server and put in the cache. At that point,
# the cache contents are VALID, DIRTY/NOT (depending
# on whether this is for reading or writing), and the
# REFERENCE COUNT is set to 1. If multiple open's take
# place on this file, REFERENCE COUNT will be updated
# accordingly. VALID gets set to 0 if the cache is
# invalidated by a callback; however, the contents
# still might be used by a given client if the file
# is already open. Note that a callback does NOT
# prevent a client from overwriting an already opened file.
#
class cache:
    def __init__(self, name, num, solve, detail):
        pass

    def stats(self):
        pass

    def put(self, fname, data, dirty, refcnt):
        pass

    def update(self, fname, data):
        pass

    def invalidate(self, fname):
        pass

    def checkvalid(self, fname):
        pass

    def printstate(self, fname):
        pass

    def checkget(self, fname):
        pass

    def get(self, fname):
        pass

    def incref(self, fname):
        pass

    def decref(self, fname):
        pass

    def setdirty(self, fname, dirty):
        pass

    def setclean(self, fname):
        pass

    def isdirty(self, fname):
        pass

    def setvalid(self, fname):
        pass


# actions
MICRO_OPEN = 1
MICRO_READ = 2
MICRO_WRITE = 3
MICRO_CLOSE = 4


def op2name(op):
    if op == MICRO_OPEN:
        return "MICRO_OPEN"
    elif op == MICRO_READ:
        return "MICRO_READ"
    elif op == MICRO_WRITE:
        return "MICRO_WRITE"
    elif op == MICRO_CLOSE:
        return "MICRO_CLOSE"
    else:
        abort("error: bad op -> " + op)


#
# Client class
#
# Models the behavior of each client in the system.
#
#
#
class client:
    def __init__(
        self, name, cid, server, files, bias, numsteps, actions, solve, detail
    ):
        pass

    def getname(self):
        pass

    def stats(self):
        pass

    def getfile(self, fname):
        pass

    def putfile(self, fname, value):
        pass

    def invalidate(self, fname):
        pass

    def step(self, space):
        pass


#
# main program
#
def main():
    parser = OptionParser()
    parser.add_option(
        "-s",
        "--seed",
        default=0,
        help="the random seed",
        action="store",
        type="int",
        dest="seed",
    )
    parser.add_option(
        "-C",
        "--clients",
        default=2,
        help="number of clients",
        action="store",
        type="int",
        dest="numclients",
    )
    parser.add_option(
        "-n",
        "--numsteps",
        default=2,
        help="ops each client will do",
        action="store",
        type="int",
        dest="numsteps",
    )
    parser.add_option(
        "-f",
        "--numfiles",
        default=1,
        help="number of files in server",
        action="store",
        type="int",
        dest="numfiles",
    )
    parser.add_option(
        "-r",
        "--readratio",
        default=0.5,
        help="ratio of reads/writes",
        action="store",
        type="float",
        dest="readratio",
    )
    parser.add_option(
        "-A",
        "--actions",
        default="",
        help="client actions exactly specified, e.g., oa1:r1:c1,oa1:w1:c1 specifies two clients; each opens the file a, client 0 reads it whereas client 1 writes it, and then each closes it",
        action="store",
        type="string",
        dest="actions",
    )
    parser.add_option(
        "-S",
        "--schedule",
        default="",
        help="exact schedule to run; 01 alternates round robin between clients 0 and 1. Left unspecified leads to random scheduling",
        action="store",
        type="string",
        dest="schedule",
    )
    parser.add_option(
        "-p",
        "--printstats",
        default=False,
        help="print extra stats",
        action="store_true",
        dest="printstats",
    )
    parser.add_option(
        "-c",
        "--compute",
        default=False,
        help="compute answers for me",
        action="store_true",
        dest="solve",
    )
    parser.add_option(
        "-d",
        "--detail",
        default=0,
        help="detail level when giving answers (1:server actions,2:invalidations,4:client cache,8:extra labels); OR together for multiple",
        action="store",
        type="int",
        dest="detail",
    )
    (options, args) = parser.parse_args()

    print("ARG seed", options.seed)
    print("ARG numclients", options.numclients)
    print("ARG numsteps", options.numsteps)
    print("ARG numfiles", options.numfiles)
    print("ARG readratio", options.readratio)
    print("ARG actions", options.actions)
    print("ARG schedule", options.schedule)
    print("ARG detail", options.detail)
    print("")

    seed = int(options.seed)
    numclients = int(options.numclients)
    numsteps = int(options.numsteps)
    numfiles = int(options.numfiles)
    readratio = float(options.readratio)
    actions = options.actions
    schedule = options.schedule
    printstats = options.printstats
    solve = options.solve
    detail = options.detail

    # with specific schedule, files are all specified by a single letter in specific actions list
    # but we ignore this for now...

    zassert(
        numfiles > 0 and numfiles <= 26,
        "main: can only simulate 26 or fewer files, sorry",
    )
    zassert(
        readratio >= 0.0 and readratio <= 1.0,
        "main: read ratio must be between 0 and 1 inclusive",
    )

    # start it
    random_seed(seed)

    # files in server to begin with
    f = files(numfiles)

    # make server
    s = server(f, solve, detail)

    clients = []

    if actions != "":
        # if specific actions are specified, figure some stuff out now
        # e.g., oa1:ra1:ca1,oa1:ra1:ca1 which is list of 0's actions, then 1's, then...
        cactions = actions.split(",")
        if numclients != len(cactions):
            numclients = len(cactions)
        i = 0
        for clist in cactions:
            clients.append(
                client("c%d" % i, i, s, f, [], len(clist), clist, solve, detail)
            )
            i += 1
    else:
        # else, make random clients
        for i in range(numclients):
            clients.append(
                client(
                    "c%d" % i, i, s, f, [readratio, 1.0], numsteps, "", solve, detail
                )
            )

    # tell server about these clients
    s.setclients(clients)

    # init print out for clients
    print("%12s" % "Server", "%12s" % " ", end=" ")
    for c in clients:
        print("%13s" % c.getname(), "%13s" % " ", end=" ")
    print("")

    # main loop
    #
    # over time, pick a random client
    # have it do one thing, show what happens
    # move on to next and so forth

    s.filestats(True)

    # for use with specific schedule
    schedcurr = 0

    # check for legal schedule (must include all clients)
    if schedule != "":
        for i in range(len(clients)):
            cnt = 0
            for j in range(len(schedule)):
                curr = schedule[j]
                if int(curr) == i:
                    cnt += 1
            zassert(
                cnt != 0,
                "main: client %d not in schedule:%s, which would never terminate"
                % (i, schedule),
            )

    # RUN the schedule (either random or specified by user)
    numrunning = len(clients)
    while numrunning > 0:
        if schedule == "":
            c = pickrand(clients)
        else:
            idx = int(schedule[schedcurr])
            # print 'SCHEDULE DEBUG:: schedule:', schedule, 'schedcurr', schedcurr, 'index', idx
            c = clients[idx]
            schedcurr += 1
            if schedcurr == len(schedule):
                schedcurr = 0
        rc = c.step(clients.index(c))
        if rc == 0:
            numrunning -= 1

    s.filestats(solve)

    if printstats:
        s.stats()
        for c in clients:
            c.stats()


if __name__ == "__main__":
    main()
