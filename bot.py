#! /usr/bin/env python

import irc.bot
import irc.strings
import re
import sqlite3
import argparse
import sys


class PlusPlusBot(irc.bot.SingleServerIRCBot):
    def __init__(self, dbconn, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname,
                                            nickname)
        self.dbconn = dbconn
        self.channel = channel
        self.record = {}

        self.setup_db()

    def setup_db(self):
        self.dbconn.execute('''
                CREATE TABLE IF NOT EXISTS karma
                (key TEXT PRIMARY KEY, score INTEGER);
            ''')

        self.dbconn.isolation_level = 'EXCLUSIVE'  # prevent races on updates

    def increment_karma(self, key, increment=1):
        c = self.dbconn.cursor()

        c.execute('SELECT score FROM karma WHERE key=?', (key,))

        row = c.fetchone()

        if row is None:
            score = 0
        else:
            score = row[0]

        score += increment

        c.execute('INSERT OR REPLACE INTO karma (key, score) VALUES (?, ?)',
                  (key, score))

        self.dbconn.commit()

        return score

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("welcome")
        c.join(self.channel)

    def on_nosuchchannel(self, c, e):
        print("No such channel")

    def handle_increment(self, match):
        target = match.group(1)
        val = self.increment_karma(target)

        msg = "{}++, now at {}".format(target, val)
        self.connection.privmsg(self.channel, msg)

    commands = [(re.compile(pat), handler) for pat, handler in
                [
                    (r'^(\w+)\+\+$', handle_increment),
                ]
                ]

    def on_pubmsg(self, c, e):
        contents = e.arguments[0]
        for rx, handler in self.commands:
            match = rx.match(contents)
            if match is not None:
                handler(self, match)
                return


def main():
    parser = argparse.ArgumentParser(description='IRC karma bot')
    parser.add_argument('dbname', help='Filename for sqlite db')
    parser.add_argument('server', metavar='server[:port]')
    parser.add_argument('channel')
    parser.add_argument('nickname')

    args = parser.parse_args()

    s = args.server.split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667

    dbconn = sqlite3.connect(args.dbname)

    bot = PlusPlusBot(dbconn, args.channel, args.nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
