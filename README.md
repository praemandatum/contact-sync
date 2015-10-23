OpenXChange-Redmine Contacts Sync
=======

#### Syncs contacts from OpenXChange to Redmine ####

This script reads contacts from an OpenXChange address book and writes them
into Redmine Contacts as provided by the CRM plugin.

Company fields from a contacts are used to create a company in Redmine, if 
it doesn't already exists.

If a contact in OX is deleted, this sync will delete it from redmine as well.

Errors messages are send to a given e-mail address.

### Required packages (might be included in python default installation)

* logging
* requests
* json
* smtplib
* ConfigParser
* redmine (install with `pip install python-redmine`)

### Configuration

For sample of the configuration file see `config.ini.sample`

### Usage

See

`./sync.py -h`
 
