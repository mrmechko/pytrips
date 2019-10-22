class TripsSem(object):
    def __init__(self, features=None, default=None, type_=None, ont=None):
        self.__ont = ont
        if not features:
            features = {}
        if not default:
            default = {}
        if not type_:
            type_ = "nil"
        self.__features = features
        self.__default = default
        self.__type = type_

    @property
    def type(self):
        return self.__type

    @property
    def features(self):
        return {k:v for k, v in self.__features.items()}

    @property
    def default(self):
        return {k:v for k, v in self.__default.items()} 

    @property
    def sem(self):
        features = self.features
        default = self.default
        for k, v in default.items():
            features[k] = v
        return features
    
    def is_subsumed(self, other):
        """Return true if other contains a conflict on something other than type.  
           TODO: Exact match only atm - make it general
        """
        othersem = other.sem
        selfsem = self.sem
        for x in selfsem:
            if x in othersem:
                if x != "type" and othersem[x] != selfsem[x]:
                    return False
            else:
                return False
        return True

    def differs_from(self, other):
        return not (self.is_subsumed(other) and other.is_subsumed(self))

    def __str__(self):
        values = list(self.sem.items())
        if not values:
            return "({})".format(self.type)
        ellipsis = ""
        if len(values) > 2:
            ellipsis = "..."
        # TODO: the values can still be a list (ie a union or parameterized) 
        values = " ".join([":{} {}".format(k, str(v)) for k, v in values[:2]])
        return "({} {}{})".format(self.type, values, ellipsis)

    def __repr__(self):
        return "<TripsSem {}>".format(str(self))
