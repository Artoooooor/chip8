class KeyBind:
    def __init__(self, key, keyMod, command):
        self.key = key
        self.keyMod = keyMod
        self.command = command

    def __eq__(self, other):
        keysMatch = self.key == other.key
        modsMatch = self.keyMod == other.keyMod
        commandsMatch = self.command == other.command
        return keysMatch and modsMatch and commandsMatch

    def matches(self, event):
        isKey = hasattr(event, 'key') and hasattr(event, 'mod')
        return isKey and self.key == event.key and self.keyMod == event.mod

    def __str__(self):
        return self.__get_str(' ')

    def __repr__(self):
        return self.__get_str(',')

    def __get_str(self, separator):
        return separator.join([str(self.key), str(self.keyMod), self.command])


def find_command(binds, event):
    for bind in binds:
        if bind.matches(event):
            return bind.command
    return None
