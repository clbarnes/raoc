# raoc

Script to automate random acts of coffee: random scheduled meetups within a group.

Use `data/` directory to store e.g. list of people, SMTP configuration.

- List of people should have email address, then some non-newline whitespace, then name, on each line
- SMTP configuration is a YAML file with keys
  - `sender` (the pre-`@` bit of a gmail address)
  - `password` (the gmail password for that account)
  - `admin` (name of administrator, possibly contact details is the sender is no-reply)

Note that the gmail account must [allow less secure apps](https://support.google.com/accounts/answer/6010255).
