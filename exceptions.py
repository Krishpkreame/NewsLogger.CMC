class CMCError(Exception):
    pass


class EnvironmentVariableNotFound(Exception):
    pass


class DatabaseError(Exception):
    pass


class NotRunningError(Exception):
    pass


class AlreadyRunningError(Exception):
    pass
