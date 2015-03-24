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

### Required packages

* logging
* requests
* json
* smtplib
* configparser

### Configuration

Configuration is done in `config.ini`

### Usage

`./sync.py [CONFIG]`
 
 If no `[CONFIG]` file is given, `config.ini` will be used.