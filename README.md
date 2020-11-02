# random acts of coffee

Script to automate random acts of coffee: scheduled pair meetups within a group.

- List of people should have email address, then some non-newline whitespace, then name, on each line
- SMTP configuration is a YAML file with keys
  - `sender` (the pre-`@` bit of a gmail address)
  - `password` (the gmail password for that account)
  - `admin` (name of administrator, possibly contact details if the sender is no-reply)

Note that the gmail account must [allow less secure apps](https://support.google.com/accounts/answer/6010255).

Depends on `strictyaml` and `yagmail`.
