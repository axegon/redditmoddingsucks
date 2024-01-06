import abc


class AbstractModeration(abc.ABC):
    @abc.abstractmethod
    def reddit(self):
        ...

    @abc.abstractmethod
    def subreddit(self):
        ...

    @abc.abstractmethod
    def fetch_mod_queue(self):
        ...

    @abc.abstractmethod
    def ban(self, user: str):
        ...
