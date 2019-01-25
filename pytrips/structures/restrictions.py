class TripsRestriction(object):
    def __init__(self, role, restrs, optionality, ont):
        self.__ont = ont
        self.__role = role
        self.__restrs = set()
        for x in restrs:
            if type(x) is list:
                self.__restrs.update(x[2:])
            if type(x) is str:
                self.__restrs.add(x)
        self.__restrs = {x.lower() for x in self.__restrs}
        self.__optionality = optionality

    @property
    def role(self):
        return self.__role.lower()

    @property
    def restrictions(self):
        return [x for x in [self.__ont[r] for r in self.__restrs] if x]

    @property
    def optionality(self):
        return self.__optionality

    def __str__(self):
        return "[:%s %s]".format(self.role, ", ".join(self.restrictions))

    def __repr__(self):
        res = ""
        if self.restrictions:
            res = self.restrictions[0]
        post = ""
        if len(self.restrictions) > 1:
            post = "and {} others".format(len(self.restrictions)-1)
        return "<TripsRestriction :{} {}{}>".format(self.role, res, post)
