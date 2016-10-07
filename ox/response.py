import logging

class Response(object):
    """Abstract response."""

    def __init__(self, raw):
        self.error_categories = raw.get("categories", [])
        if type(self.categories) is str:
            self.categories = [self.categories]
        self.error_code = raw.get("code", "")
        self.error_msg = raw.get("error", "")
        self.error_desc = raw.get("error_desc", "")
        self.error_id = raw.get("error_id", "")
        self.timestamp = raw.get("timestamp", None)



class UpdatesResponse(Response):

    def __init__(self, raw):
        super(Response, self).__init__(raw)
        self.created = created
        self.modified = modified
        self.deleted = deleted
        self.timestamp = timestamp

    @classmethod
    def parse(cls, raw, columns):
        res = cls(raw.get("timestamp"))
        data = raw.get("data")
        for e in data:
            if type(e) is list:
                # TODO: seems that creations and modifications are
                # indistinguishable at this stage, thus treat all as created
                res.created.append(cls.__dictify(e, columns))
            else:
                res.deleted.append(e)
        return res

    @classmethod
    def __dictify(cls, contact_array, columns):
        dictified = dict()
        for field, value in zip(columns, contact_array):
            if value is not None:
                dictified[int(field)] = value
        return dictified
