OpenXChange-Redmine Contacts Sync
=======

#### Syncs contacts from OpenXChange to Redmine ####

This script reads contacts from an OpenXChange address book and writes them
into Redmine Contacts. Contacts are mapped by the UID field from OpenXChange.
Since the UID field has to be searched for every contact, this script has
the runtime O(n²).

Company fields from a contacts are used to create a company in Redmine, if 
it doesn't already exists.

Errors messages are send to a given e-mail address.

### Required packages (might be included in python default installation)

* logging
* requests
* json
* smtplib
* ConfigParser
* redmine (install with `pip install python-redmine`)

### Configuration

Configuration is done in `config.ini`

### Usage

See

`./sync.py -h`
 
