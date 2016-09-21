import logging
import copy

from .UserPreferencesModel import UserPreferencesModel

logger = logging.getLogger(__name__)

class UserPreferences():
    def __init__(self, config=None):
        self.__users = dict()
        self.__config = config

    def __checkUser(self,userid):
        if self.__config is None:
            logger.error('Configuration file is needed')
            return None
        if userid in self.__users:
            return True
        else:
            self.__users[userid] = UserPreferencesModel(userid,self.__config)
            return False

    def add_config(self,config):
        self.__config = config
        logger.info('Configuration file set')

    def get(self,userid):
        result = self.__checkUser(userid)
        if result is None:
            logger.info('Failed')
            return  None
        if not result:
            logger.info('Adding user %s',userid)
        return self.__users[userid]

    def rem(self,userid):
        if userid in self.__users:
            del self.__users[userid]
            logger.info('User %s has been removed' % userid)
        else:
            logger.info('User %s does not exist' % userid)

    @property
    def config(self):
        return copy.deepcopy(self.__config)
