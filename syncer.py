#!/usr/bin/env python
# coding: utf-8

import logging
from redmine import Redmine
from redmine.exceptions import ResourceAttrError

import ox
import ox.session
import ox.loader

class ContactSyncer(object):
    def __init__(self, **kwargs):
        self.ox_base = kwargs.get("ox_base")
        self.ox_user = kwargs.get("ox_user")
        self.__ox_password = kwargs.get("ox_password")
        self.ox_folder = kwargs.get("ox_folder")
        self.ox_columns = kwargs.get("ox_columns")
        self.redmine_base = kwargs.get("redmine_base")
        self.__redmine_key = kwargs.get("redmine_key")
        self.redmine_project = kwargs.get("redmine_project")
        self.no_act = False
        self.id_field_id = kwargs.get("redmine_cf_id")
        self.uid_field_id = kwargs.get("redmine_cf_uid")
        self.oxurl_field_id = kwargs.get("redmine_cf_oxurl")

    def sync(self, lastrun=0):
        ox_contacts = self.__get_ox_contacts(lastrun)
        if ox_contacts.timestamp != 0:
            logging.debug("Applying updates to redmine")
            self.__write_contact_updates(ox_contacts)
        else:
            # no changes since last sync attempt
            # no need to write anything to redmine
            logging.info("No changes")
        return ox_contacts.timestamp

    def __get_ox_contacts(self, since):
        session = ox.session.OXSession(self.ox_base, self.ox_user, self.__ox_password)
        session.establish()
        try:
            loader = ox.loader.OXContactLoader(session, self.ox_folder, self.ox_columns)
            contacts = loader.loadUpdates(since)
        finally:
            session.logout()
        return contacts

    def __write_contact_updates(self, ox_contacts):
        logging.debug("Fetch contacts from redmine")
        redmine = Redmine(self.redmine_base, key=self.__redmine_key)
        contacts = redmine.contact.all()
        index, index_oxid, company_set = self.__build_index(contacts)
        logging.debug("Add or modify {} contacts".format(len(ox_contacts.created)))
        num_created = 0
        for ox_contact in ox_contacts.created:
            red_contact = index.get(ox_contact.get(ox.UID))
            if red_contact is None:
                # no contact with this uid in redmine
                # create new one
                logging.debug("OX contact with id {} and uid {} not found. Create.".format(ox_contact.get(ox.ID), ox_contact.get(ox.UID)))
                num_created += 1
                red_contact = redmine.contact.new()
            self.__adopt_contact(red_contact, ox_contact)
            # create a new contact for the company if necessary
            try:
                company = red_contact.company
            except ResourceAttrError as e:
                company = ""
            if company is not "":
                company = company.strip()
                if company not in company_set and self.no_act is False:
                    logging.debug(u"Create company {}.".format(company))
                    redmine.contact.create(
                        first_name=company,
                        is_company=True,
                        project_id=self.redmine_project
                    )
            if not self.no_act:
                try:
                    red_contact.save()
                except Exception as e:
                    logging.exception("Failed to save OX contact %s: %s",
                            ox_contact.get(ox.ID), str(ox_contact))

        logging.debug("Delete {} contacts".format(len(ox_contacts.deleted)))
        for del_id in ox_contacts.deleted:
            red_contact = index_oxid.get(del_id)
            if red_contact is not None:
                if not self.no_act:
                    redmine.contact.delete(red_contact.id)
            else:
                logging.debug("Contact {} should be deleted but could not be found.".format(del_id))

        logging.info("{} contacts actually were created.".format(num_created))


    def __adopt_contact(self, red_contact, ox_contact):
        red_contact.project_id = self.redmine_project
        red_contact.first_name = ox_contact.get(ox.FIRST_NAME, "n.v.").strip() # fn is mandatory
        title = ox_contact.get(ox.TITLE, "").strip()
        if title != "":
            red_contact.first_name = title + " " + red_contact.first_name
        if red_contact.first_name == "":
            red_contact.first_name = "n.v."
        red_contact.last_name = ox_contact.get(ox.LAST_NAME, "").strip()
        red_contact.middle_name = ox_contact.get(ox.SECOND_NAME, "").strip()
        red_contact.phones = [p.strip() for p in [
            ox_contact.get(ox.TELEPHONE_BUSINESS1)
        ] if p is not None]
        red_contact.emails = [e.strip() for e in [
            ox_contact.get(ox.EMAIL1),
            ox_contact.get(ox.EMAIL2),
            ox_contact.get(ox.EMAIL3)
        ] if e is not None]
        red_contact.address_attributes = {
            "street1": ox_contact.get(ox.STREET_BUSINESS, "").strip(),
            "postcode": ox_contact.get(ox.POSTAL_CODE_BUSINESS, "").strip(),
            "city": ox_contact.get(ox.CITY_BUSINESS, "").strip(),
            "region": ox_contact.get(ox.STATE_BUSINESS, "").strip(),
            "country_code": ox_contact.get(ox.COUNTRY_BUSINESS, "").strip(),
        }
        red_contact.company = ox_contact.get(ox.COMPANY, "").strip()
        red_contact.background = "\n".join([i.strip() for i in [
            ox_contact.get(ox.USERFIELD01),
            ox_contact.get(ox.USERFIELD02),
            ox_contact.get(ox.NOTE)
        ] if i is not None])
        red_contact.job_title = ox_contact.get(ox.PROFESSION, "").strip()
        if red_contact.is_new:
            # only new to make this reentrant to keep redmine tags
            red_contact.tag_list = [t.strip() for t in [
                ox_contact.get(ox.USERFIELD03),
                ox_contact.get(ox.USERFIELD04)
            ] if t is not None]
        red_contact.website = ox_contact.get(ox.URL, "").strip()
        self._adopt_ids(red_contact, ox_contact.get(ox.ID), ox_contact.get(ox.UID))

    def _adopt_ids(self, red_contact, oxid, uid):
        red_contact.custom_fields = [
            {"id": self.id_field_id, "value": oxid},
            {"id": self.uid_field_id, "value": uid},
            #{"value": get_ox_contact_website(ox_contact), "name": settings.name_ox_website, "id": settings.ox_website_field_id}
        ]

    def _get_id(self, red_contact):
        field = red_contact.custom_fields.get(self.id_field_id)
        return field.value if field is not None and field != "" else None

    def _get_uid(self, red_contact):
        field = red_contact.custom_fields.get(self.uid_field_id)
        return field.value if field is not None and field != "" else None

    def __build_index(self, contacts):
        index = dict()
        index_oxid = dict()
        company_set = set()
        for contact in contacts:
            try:
                company_set.add(contact.company.strip())
            except ResourceAttrError as e:
                pass
            uid = self._get_uid(contact)
            if uid is None:
                # Has no uid custom field, probably not created by sync
                logging.debug("Redmine contact {} has no uid.".format(contact.id))
                continue
            index[uid] = contact
            oxid = self._get_id(contact)
            if oxid is None:
                # Contacts synced by an older version of this script might not have the id set
                logging.debug("Redmine contact {} has no oxid.".format(contact.id))
            elif isinstance(oxid, int) and oxid is 0:
                # redmine may use 0 as default for a unset customfield
                # ignore these
                pass
            else:
                try:
                    oxid = int(oxid)
                except ValueError as e:
                    logging.debug("Non-integer oxid {} for contact {}".format(oxid, contact.id))
                else:
                    index_oxid[oxid] = contact
        return (index, index_oxid, company_set)



class ContactSyncerForLight(ContactSyncer):
    """Contact syncer for light CRM version for relying on custom fields."""
    def __init__(self, **kwargs):
        super(ContactSyncerForLight, self).__init__(**kwargs)

    def _adopt_ids(self, red_contact, oxid, uid):
        red_contact.skype_name = oxid
        red_contact.website = uid

    def _get_id(self, redmine_contact):
        try:
            return redmine_contact.skype_name
        except ResourceAttrError:
            return None

    def _get_uid(self, redmine_contact):
        try:
            return redmine_contact.website
        except ResourceAttrError:
            return None
