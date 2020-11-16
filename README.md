# random acts of coffee

Script to automate random acts of coffee: scheduled pair meetups within a group.

- List of people should have email address, some non-newline whitespace, interval, whitespace, name
  - "I want a new partner every {interval} week(s)" - options should be multiples of each other (e.g. 1, 2, 4)
- SMTP configuration is a YAML file with keys
  - `sender` (the pre-`@` bit of a gmail address)
  - `password` (the gmail password for that account)
  - `admin` (name of administrator, possibly contact details if the sender is no-reply)

Note that the gmail account must [allow less secure apps](https://support.google.com/accounts/answer/6010255).

Depends on `strictyaml` and `yagmail`.
