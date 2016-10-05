import logging
import copy

from .UserPreferencesModel import UserPreferencesModel

logger = logging.getLogger(__name__)


class UserPreferences:
    def __init__(self, config=None):
        self.__users = dict()
        self.__config = config

    def __check_user(self, chat_id):
        if self.__config is None:
            logger.error('Failed due to configuration file not set.')
            return None
        if chat_id in self.__users:
            return True
        else:
            self.__users[chat_id] = UserPreferencesModel(chat_id, self.__config)
            return False

    def add_config(self, config):
        self.__config = config
        logger.info('Configuration file set')

    def get(self, chat_id):
        result = self.__check_user(chat_id)
        if result is None:
            logger.error('Failed due to configuration file not set.')
            return None
        if not result:
            logger.info('Adding user %s.', chat_id)
        return self.__users[chat_id]

    def rem(self, chat_id):
        if chat_id in self.__users:
            del self.__users[chat_id]
            logger.info('User %s has been removed.' % chat_id)
        else:
            logger.info('User %s does not exist.' % chat_id)

    @property
    def config(self):
        return copy.deepcopy(self.__config)

    def users(self):
        return list(self.__users.keys())
