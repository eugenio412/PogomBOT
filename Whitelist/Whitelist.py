import logging
import sys, os, copy, tempfile
import errno
import json

logger = logging.getLogger(__name__)

class Whitelist(object):
	def __init__(self, config):
		self.__loadedconfig = config
		self.__admins = self.__loadedconfig.get('LIST_OF_ADMINS', [])
		self.__filename = "whitelist.json"
		
		self.__whitelistEnabled = len(self.__admins) != 0
		self.__whitelist = []
		if self.__whitelistEnabled:
			logger.info('Whitelist enabled.')
			self.__load_whitelist()
		else:
			logger.info('Whitelist disabled. No admins configured.')

	def isWhitelistEnabled(self):
		return self.__whitelistEnabled

	def isAdmin(self, userName):
		return not self.isWhitelistEnabled() or (userName in self.__admins)

	def isWhitelisted(self, userName):
		return self.isAdmin(userName) or (userName in self.__whitelist)

	def addUser(self, userName):
		if self.isWhitelistEnabled() and (userName not in self.__whitelist):
			logger.info('Adding <%s> to whitelist.' % (userName))
			self.__whitelist.append(userName)
			self.__save_whitelist()
			return True
		return False

	def remUser(self, userName):
		if self.isWhitelistEnabled() and (userName in self.__whitelist):
			logger.info('Removing <%s> from whitelist.' % (userName))
			self.__whitelist.remove(userName)
			self.__save_whitelist()
			return True
		return False

	def __getDefaulteDir(self):
		directory = os.path.join(
		os.path.dirname(sys.argv[0]), "serverdata")
		try:
			os.makedirs(directory)
		except OSError as e:
			if e.errno != errno.EEXIST:
				logger.error('Unable to create serverdata directory.')
		return directory

	def __load_whitelist(self):
		fullpath = os.path.join(self.__getDefaulteDir(), self.__filename)

		logger.info('Whitelist loading.')
		self.__whitelist = []
		if os.path.isfile(fullpath):
			try:
				with open(fullpath, 'r', encoding='utf-8') as f:
					self.__whitelist = json.load(f)
				logger.info('Whitelist loaded successful.')
			except Exception as e:
				logger.error(e)
		else:
			logger.warn('No whitelist file present.')
			self.__whitelist = []

	def __save_whitelist(self):
		fullpath = os.path.join(self.__getDefaulteDir(), self.__filename)

		logger.info('Whitelist saving.')
		try:
			with open(fullpath, 'w', encoding='utf-8') as file:
				json.dump(self.__whitelist, file, indent=4, sort_keys=True, separators=(',', ':'))
			logger.info('Whitelist saved  successful.')
		except Exception as e:
			logger.warn('Error while saving whitelist. (%s)' % (e))