

class BackupsException(Exception):
    pass


class NextCloudBackupsException(BackupsException):
    pass


class NextCloudClientException(NextCloudBackupsException):
    pass