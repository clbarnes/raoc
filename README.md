# random acts of coffee

Script to automate random acts of coffee: scheduled pair meetups within a group.

A non-functional example configuration exists in [`/example`](./example), and includes:

- List of participants, including an email address, some non-newline whitespace, interval, whitespace, name
  - "I want a new partner every {interval} week(s)" - options should be multiples of each other (e.g. 1, 2, 4)
- SMTP configuration for sending gmail address, a YAML file with keys
  - `sender` (the pre-`@` bit of a gmail address)
  - `password` (the gmail password for that account)
  - `admin` (name of administrator, possibly contact details if the sender is no-reply)

Note that the sending gmail account must [allow less secure apps](https://support.google.com/accounts/answer/6010255).

The script is deterministic based on the date, to day resolution (defaults to the date of the system time).

## Installation

Written for python 3.9; may work with some lower versions.

```sh
cd path/to/this/dir
pip install .
```

This will install a script

## Usage

```help
usage: raoc.py [-h] [--handle-odd] [--smtp SMTP] [--date DATE] people

positional arguments:
  people                Path to file whose rows are email address, interval,
                        then name (whitespace-separated)

optional arguments:
  -h, --help            show this help message and exit
  --handle-odd, -o      If there are an odd number of people, double up one
                        person to include everyone
  --smtp SMTP, -s SMTP  Path to YAML file containing SMTP configuration to
                        send emails to everyone involved
  --date DATE, -d DATE  Date to run, as ISO-8601, for testing purposes
                        (default: today)
```

An example shell script to match people up and email out, recording the output and log messages:

```sh
#!/bin/sh
# ~/raoc_script.sh

cd ~/raoc
mkdir -p data/log data/history
source env/bin/activate

raoc \
  data/people.tsv \
  --smtp data/smtp.yaml \
  --handle-odd \
  2> data/log/$(date --iso-8601).log \
  1> data/history/$(date --iso-8601).tsv
```

An example [crontab line](https://en.wikipedia.org/wiki/Cron) to run that script at 08:30 every Monday:

```crontab
# crontab -e
# min  hr  mnthday  mnth  wkday  command
30     8   *        *     MON    bash ~/raoc_script.sh
```
