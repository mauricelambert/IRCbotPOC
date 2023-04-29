#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This file implements a little POC for an IRC bot.
#    Copyright (C) 2023  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This file implements a little POC for an IRC bot.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This file implements a little POC for an IRC bot.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/IRCbotPOC"

copyright = """
IRCbotPOC  Copyright (C) 2023  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["IrcBot"]

print(copyright)

from typing import Tuple, Iterable
from socket import socket
from sys import stdout


class IrcBot:
    def __init__(self, host: str, port: int = 6667):
        self.host = host
        self.port = port
        self.address = (host, port)
        self.socket: socket = None
        self.joined: str = None

    def __enter__(self):
        sock = self.socket = socket()
        sock.connect(self.address)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()

    def send_user(
        self, user: str, mode: int = 0, realname: str = "Python IRC Bot"
    ) -> None:
        self.send(f"USER {user} {mode} * :{realname}")

    def send_nick(self, nick: str) -> None:
        self.send(f"NICK {nickname}")

    def send_join(self, channel: str) -> None:
        channel = "#" + channel
        self.joined = channel
        while self.joined:
            self.send(f"JOIN {channel}")
            self.recv()

    def start(
        self,
        username: str,
        channels: Tuple[str],
        nick: str = None,
        realname: str = "Python IRC Bot",
        mode: int = 0,
    ) -> str:
        self.send_user(username, mode, realname)
        self.recv()
        self.send_nick(nick or username)
        self.recv()
        for channel in channels:
            self.send_join(channel)
        return self.recv()

    def send_pong(self, ping: str) -> None:
        self.send(f"PONG {ping.split()[1]}")

    def send_privmsg(self, targets: Iterable[str], message: str) -> None:
        self.send(f"PRIVMSG {','.join(targets)} :{message}")

    def handle(self, line: str) -> None:
        splitted_line = line.split()
        if line.startswith("PING "):
            self.send_pong(line)
        elif splitted_line[1] == "PRIVMSG":
            user = line[1:].split("!")[0]
            channel = splitted_line[2]
            message = line.split(maxsplit=3)[-1].strip()[1:]
            print(f"{user!r} send {message!r} on {channel!r}")
            self.send_privmsg(
                (user, "#test"), f"{user!r} send {message!r} on {channel!r}"
            )
        elif (
            self.joined
            and len(splitted_line) == 3
            and splitted_line[1] == "JOIN"
            and splitted_line[2].lstrip(":") == self.joined
        ):
            self.joined = None

    def recv(self) -> str:
        def do_recv(data: bytes) -> str:
            stdout.buffer.write(data)
            data = data.decode("ascii")
            for line in data.splitlines():
                self.handle(line)
            return data

        data = do_recv(self.socket.recv(65535))
        self.socket.setblocking(False)

        while True:
            try:
                line = self.socket.recv(65535)
            except BlockingIOError:
                break
            else:
                data += do_recv(line)

        self.socket.setblocking(True)
        stdout.flush()
        return data

    def send(self, message: str) -> None:
        message = message.encode("ascii") + b"\r\n"
        self.socket.sendall(message)
        stdout.buffer.write(message)
        stdout.flush()


nickname = "MyPythonIRCbot"
channels = ("test",)
mode = 8  # mode invisible
mode = 0

with IrcBot("chat.freenode.net", 6667) as irc_connection:
    irc_connection.start(nickname, channels)
    while True:
        data = irc_connection.recv()
