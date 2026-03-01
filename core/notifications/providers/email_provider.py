from abc import ABC, abstractmethod


class EmailProvider(ABC):

    @abstractmethod
    def send(self, recipients: list[str], subject: str, body: str):
        pass