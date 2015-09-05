#! /usr/bin/env python

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import re

class PlusPlusBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.record = {}

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    commands = [(re.compile(pat), handler) for pat, handler in
        [
            (r'^(\w+)\+\+$', self.handle_increment),
        ]
    ]

    def handle_increment(self, match):
        target = match.group(1)
        val = self.record.get(target, 0) + 1
        self.record[target] = val

        msg = "{}++, now at {}".format(target, val)
        self.connection.privmsg(channel, msg)

    def on_pubmsg(self, c, e):
        contents = e.arguments[0]
        print contents
        for rx, handler in commands:
            match = rx.match(contents)
            if match is not None:
                handler(match)
                return

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = PlusPlusBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
