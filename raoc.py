#!/usr/bin/env python
from argparse import ArgumentParser
from typing import Iterator, NamedTuple, Iterable, Tuple
import random
import datetime as dt
import logging

import yagmail
import strictyaml as syml

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.DEBUG


def parse_args(args=None):
    parser = ArgumentParser()

    parser.add_argument(
        "people", help="Path to file whose rows are email address and then name"
    )
    # parser.add_argument("--history", "-h", help="Path to TSV file with rows containing date and two email addresses matched")
    parser.add_argument(
        "--smtp",
        "-s",
        help="Path to YAML file containing SMTP configuration to send emails to everyone involved",
    )
    return parser.parse_args(args)


class Person(NamedTuple):
    email: str
    name: str

    def __str__(self):
        return f"{self.name} <{self.email}>"


def read_people(fpath) -> Iterator[Tuple[str, str]]:
    with open(fpath) as f:
        for line in f:
            yield Person(*line.strip().split(maxsplit=1))


def match_people(people: Iterable[Person], seed=None):
    rand = random.Random(seed)
    shuffled = list(people)
    rand.shuffle(shuffled)

    while len(shuffled) >= 2:
        yield tuple(sorted((shuffled.pop(), shuffled.pop())))


def main(args=None):
    logging.basicConfig(level=DEFAULT_LOG_LEVEL)

    args = parse_args(args)
    matches = list(match_people(read_people(args.people)))

    if args.smtp:
        emailer = Emailer.from_yaml(args.smtp)
        emailer.send_pairs(matches)

    for p1, p2 in matches:
        print(f"{p1}\t{p2}")


MSG_TEMPLATE = """
Hi {recipient_name},

This is an automated email to suggest that you meet a labmate for a chat this week.

Get in contact with {partner_name} at {partner_email}.

Have fun!
{admin}
""".strip()


class Emailer:
    def __init__(self, sender, password, admin):
        self.sender = sender
        self.admin = admin
        self.password = password

    def create_message(self, recipient: Person, partner: Person) -> Tuple[str, str]:
        today = dt.date.today().isoformat()
        content = MSG_TEMPLATE.format(
            recipient_name=recipient.name,
            partner_name=partner.name,
            partner_email=partner.email,
            admin=self.admin,
        )
        subject = f"Random Acts of Coffee {today}: {partner.name}"
        return subject, content

    def send_pairs(self, pairs: Iterable[Tuple[Person, Person]]):
        server = yagmail.SMTP(self.sender, self.password)
        for pair in pairs:
            for recipient, partner in [pair, pair[::-1]]:
                subject, msg = self.create_message(recipient, partner)
                logger.debug("Sending email to %s", recipient.email)
                server.send(recipient.email, subject, msg)

    @classmethod
    def from_yaml(cls, fpath):
        schema = syml.Map(
            {
                "password": syml.Str(),
                "sender": syml.Str(),
                "admin": syml.Str(),
            }
        )
        with open(fpath) as f:
            d = syml.load(f.read(), schema).data
        return cls(**d)


if __name__ == "__main__":
    main()
