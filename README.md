# random acts of coffee

Script to automate random acts of coffee: scheduled pair meetups within a group.

- List of people should have email address, some non-newline whitespace, interval, whitespace, name
  - "I want a new partner every {interval} week(s)" - options should be multiples of each other (e.g. 1, 2, 4)
- SMTP configuration is a YAML file with keys
  - `sender` (the pre-`@` bit of a gmail address)
  - `password` (the gmail password for that account)
  - `admin` (name of administrator, possibly contact details if the sender is no-reply)

Note that the gmail account must [allow less secure apps](https://support.google.com/accounts/answer/6010255).

## Usage

```help
usage: raoc [-h] [--handle-odd] [--smtp SMTP] people

positional arguments:
  people                Path to file whose rows are email address and then
                        name

optional arguments:
  -h, --help            show this help message and exit
  --handle-odd, -o      If there is an odd number of people, double up one
                        person to include everyone
  --smtp SMTP, -s SMTP  Path to YAML file containing SMTP configuration to
                        send emails to everyone involved
```

A shell script and crontab line to match people and email out the pairings at 08:30 every week:

```sh
#!/bin/sh
# ~/raoc_script.sh

cd ~/raoc
mkdir -p data/log data/history
env/bin/python raoc.py \
  data/people.tsv \
  --smtp data/smtp.yaml \
  --handle-odd \
  2> data/log/$(date --iso-8601).log \
  1> data/history/$(date --iso-8601).tsv
```

```crontab
# crontab -e
# min  hr  mnthday  mnth  wkday  command
30     8   *        *     MON    ~/raoc_script.sh
```
