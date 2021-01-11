#!/usr/bin/env python
from argparse import ArgumentParser
from typing import Iterator, NamedTuple, Iterable, Tuple, List, Optional
import random
import datetime as dt
import logging

import yagmail
import strictyaml as syml

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.DEBUG
TODAY = dt.date.today()


def parse_args(args=None):
    parser = ArgumentParser()

    parser.add_argument(
        "people",
        help="Path to file whose rows are email address, interval, then name (whitespace-separated)",
    )
    # parser.add_argument("--history", "-h", help="Path to TSV file with rows containing date and two email addresses matched")
    parser.add_argument(
        "--handle-odd",
        "-o",
        action="store_true",
        help="If there are an odd number of people, double up one person to include everyone",
    )
    parser.add_argument(
        "--smtp",
        "-s",
        help="Path to YAML file containing SMTP configuration to send emails to everyone involved",
    )
    parser.add_argument(
        "--date",
        "-d",
        type=dt.date.fromisoformat,
        default=TODAY,
        help="Date to run, as ISO-8601, for testing purposes (default: today)",
    )
    return parser.parse_args(args)


class Person(NamedTuple):
    email: str
    name: str

    def __str__(self):
        return f"{self.name} <{self.email}>"

    def long_str(self):
        return f"{self.name} at {self.email}"


def week_num(date: dt.date):
    day_since_1 = date.toordinal()
    return day_since_1 // 7


def read_people(fpath, date: dt.date = TODAY) -> Iterator[Person]:
    with open(fpath) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            email, interval_name = line.split(maxsplit=1)
            try:
                interval, name = interval_name.split(maxsplit=1)
                if week_num(date) % int(interval):
                    logger.info("Skipped %s due to off week", Person(email, name))
                    continue
            except ValueError:
                # no number was given
                name = interval_name
            yield Person(email, name)


def chunk(it: Iterable, size: int = 2, sort=False):
    out = []
    for item in it:
        out.append(item)
        if len(out) >= size:
            if sort:
                yield sorted(out)
            else:
                yield out
            out = []

    if out:
        if sort:
            out = sorted(out)
        yield out


class PeopleMatcher:
    def __init__(self, people: Iterable[Person], seed=TODAY):
        self.people = list(people)
        self.rand = random.Random(seed.toordinal())
        first_random = self.rand.random()
        logger.debug("First random number is %s", first_random)

    def shuffle(
        self, handle_odd=False, sort=True
    ) -> Tuple[List[Tuple[Person, Person]], Optional[Person]]:
        ppl = list(self.people)
        self.rand.shuffle(ppl)
        leftover = None
        if len(ppl) % 2:
            if handle_odd:
                ppl.append(ppl[0])
            else:
                leftover = ppl.pop()
        out = list(chunk(ppl, 2, sort))
        if sort:
            out = sorted(out)
        return out, leftover


def match_people(people: Iterable[Person], seed=None):
    rand = random.Random(seed)
    shuffled = list(people)
    rand.shuffle(shuffled)

    while len(shuffled) >= 2:
        yield tuple(sorted((shuffled.pop(), shuffled.pop())))


MSG_TEMPLATE = """
Hi {recipient_name},

This is an automated email to suggest that you meet a labmate for a chat this week.

Get in contact with {partner}.

Have fun!
The Coffee Elves

Contact {admin} if there are any problems.
""".strip()

ODD_TEMPLATE = """
Hi {recipient_name},

This is an automated email.
Unfortunately, as there are an odd number of people involved in the lab's Random Acts of Coffee, you could not be assigned a partner this week.

See you next week!
The Coffee Elves

Contact {admin} if there are any problems.
""".strip()


class Emailer:
    def __init__(self, sender, password, admin_email, date: dt.date = TODAY):
        self.sender = sender
        self.admin_email = admin_email
        self.password = password
        self.datestamp = date.isoformat()

    def create_message(self, recipient: Person, partner: Person) -> Tuple[str, str]:
        content = MSG_TEMPLATE.format(
            recipient_name=recipient.name,
            partner=partner.long_str(),
            admin=self.admin_email,
        )
        subject = f"Random Acts of Coffee {self.datestamp}: {partner.name}"
        return subject, content

    def create_odd_message(self, recipient: Person) -> Tuple[str, str]:
        content = ODD_TEMPLATE.format(
            recipient_name=recipient.name, admin=self.admin_email
        )
        subject = f"Random Acts of Coffee {self.datestamp}: Week off"
        return subject, content

    def server(self):
        return yagmail.SMTP(self.sender, self.password)

    def send_pairs(self, pairs: Iterable[Tuple[Person, Person]]):
        server = self.server()
        for pair in pairs:
            for recipient, partner in [pair, pair[::-1]]:
                subject, msg = self.create_message(recipient, partner)
                logger.debug("Sending pair email to %s", recipient.email)
                server.send(recipient.email, subject, msg)

    def send_odd(self, recipient: Person):
        server = self.server()
        subject, msg = self.create_odd_message(recipient)
        logger.debug("Sending odd email to %s", recipient.email)
        server.send(recipient.email, subject, msg)

    @classmethod
    def from_yaml(cls, fpath, date: dt.date = TODAY):
        schema = syml.Map(
            {
                "password": syml.Str(),
                "sender": syml.Str(),
                "admin_email": syml.Str(),
            }
        )
        with open(fpath) as f:
            d = syml.load(f.read(), schema).data
        return cls(**d)


def main(args=None):
    logging.basicConfig(level=DEFAULT_LOG_LEVEL)

    args = parse_args(args)
    logger.debug("Args: %s", args)
    logger.debug("Effective date is %s", args.date)
    people = read_people(args.people, args.date)
    matcher = PeopleMatcher(people, seed=args.date)
    matches, odd = matcher.shuffle(args.handle_odd)

    if args.smtp:
        emailer = Emailer.from_yaml(args.smtp, args.date)
        emailer.send_pairs(matches)
        if odd:
            emailer.send_odd(odd)

    for p1, p2 in matches:
        print(f"{p1}\t{p2}")
    if odd:
        print(str(odd))


if __name__ == "__main__":
    main()
