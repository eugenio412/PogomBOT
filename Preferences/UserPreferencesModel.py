#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This is a preference management getter and setter class which manages the user preferences.
#
# This work is based on the pypref module of Bachir Aoun <https://www.linkedin.com/in/bachiraoun> and modified for json
# and dictionary cases. The original code can be found at: https://github.com/bachiraoun/pypref and is protected under
# the AGPL-3.0 licencing, which can be found at https://github.com/bachiraoun/pypref/blob/master/LICENSE.txt
#
# Simon Ward 17/09/2016


import copy
import errno
import json
import logging
import os
import sys
import tempfile

logger = logging.getLogger(__name__)


class UserPreferencesModel(object):
    def __default_dict(self):
        global config
        preferences = dict(
            location=[None, None, None],
            language=self.loadedconfig.get('DEFAULT_LANG', 'en'),
            search_ids=[]
        )
        return preferences

    def __init__(self, chat_id, config_in):
        self.chat_id = chat_id
        self.loadedconfig = config_in
        self.__set_directory(directory=self.__get_default_dir())
        self.__set_filename(filename=self.__get_default_filename(chat_id))
        # load existing or create file
        self.__load_or_create(False)
        logger.info('[%s] Created new preferences.' % self.chat_id)

    def __get_default_dir(self):
        user_path = os.path.join(
            os.path.dirname(sys.argv[0]), "userdata")
        try:
            os.makedirs(user_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error('Unable to make preference directory')
        return user_path

    def __get_default_filename(self, chat_id):
        return '%s.json' % chat_id

    def __getitem__(self, key):
        return dict.__getitem__(self.__preferences, key)

    def __set_directory(self, directory):
        if directory is None:
            directory = os.path.expanduser('~')
        else:
            assert os.path.isdir(directory), "Given directory '%s' is not an existing directory" % directory
        # check if a directory is writable
        try:
            testfile = tempfile.TemporaryFile(dir=directory)
            testfile.close()
        except Exception as e:
            raise Exception("Given directory '%s' is not a writable directory." % directory)
        # set directory
        self.__directory = directory

    def __set_filename(self, filename):
        assert isinstance(filename, str), "filename must be a string, '%s' is given." % filename
        filename = str(filename)
        assert os.path.basename(filename) == filename, "Given filename '%s' is not valid. \
A valid filename must not contain especial characters or operating system separator which is '%s' in this case." % (
            filename, os.sep)
        if not filename.endswith('.json'):
            filename += '.json'
            logging.warning("[%s] '.json' appended to given filename '%s'" % (self.chat_id, filename))
        self.__filename = filename

    def __load_or_create(self, sw):
        # Do we load or create new
        if sw:
            # We load
            fullpath = self.fullpath
            if os.path.isfile(fullpath):
                # The user has a preference file
                logger.info('[%s] loadUserConfig.' % self.chat_id)
                try:
                    if os.path.isfile(fullpath):
                        with open(fullpath, 'r', encoding='utf-8') as f:
                            preferences = json.load(f)
                    else:
                        logger.warn('[%s] loadUserConfig. File not found!' % self.chat_id)
                        preferences = self.__default_dict()
                        pass
                except Exception as e:
                    logger.error('[%s] %s' % (self.chat_id, e))
                    preferences = self.__default_dict()
                self.__preferences = preferences
            else:
                # The user does not have a preference file. Create one
                self.__preferences = self.__default_dict()
                self.__dump_file()
        else:
            # Just create in memory
            self.__preferences = self.__default_dict()
            # self.__dump_file()

    def __dump_file(self, temp=False):

        # Clear out program data.......
        pref_loc = self.__preferences

        if temp:
            try:
                fd = tempfile.NamedTemporaryFile(dir=tempfile._get_default_tempdir(), delete=True)
            except Exception as e:
                logger.warn('[%s] Unable to create preferences temporary file. (%s)' % (self.chat_id, e))
                raise Exception("Unable to create preferences temporary file. (%s)" % e)
        else:
            # try to open preferences file
            try:
                fd = open(self.fullpath, 'w', encoding='utf-8')
            except Exception as e:
                logger.warn('[%s] Unable to open preference file for writing. (%s)' % (self.chat_id, e))
                raise Exception("Unable to open preferences file '%s." % self.fullpath)
        try:
            with fd:
                json.dump(pref_loc, fd, indent=4, sort_keys=True, separators=(',', ':'))
        except Exception as e:
            logger.error('[%s] Unable to write to preferences file. (%s)' % (self.chat_id, e))
            raise Exception("Unable to write preferences to file '%s." % self.fullpath)
        # close file
        fd.close()

    def __is_updated(self, pref_loc):
        values = iter(pref_loc.values())
        first = next(values)
        if all(first == item for item in self.preferences):
            return 0
        else:
            return 1

    @property
    def directory(self):
        """Preferences file directory."""
        return copy.deepcopy(self.__directory)

    @property
    def filename(self):
        """Preferences file name."""
        return copy.deepcopy(self.__filename)

    @property
    def fullpath(self):
        """Preferences file full path."""
        return os.path.join(self.__directory, self.__filename)

    @property
    def preferences(self):
        """Preferences dictionary copy."""
        return copy.deepcopy(self.__preferences)

    def get(self, key, default=None):
        """
        Get the preferences value for the given key.
        If key is not available then returns then given default value.

        :Parameters:
            #. key (object): The Key to be searched in the preferences.
            #. default (object): The Value to be returned in case key does not exist.

        :Returns:
            #. value (object): The value of the given key or given default value is
               key does not exist.
        """
        return self.__preferences.get(key, default)

    def check_preferences(self, preferences):
        """
        This is an abstract method to be overloaded if needed.
        All preferences setters such as set_preferences and update_preferences
        call check_preferences prior to setting anything. This method returns
        a check flag and a message, if the flag is False, the message is raised
        as an error like the following:

        .. code-block:: python

            flag, m = self.check_preferences(preferences)
            assert flag, m


        :Parameters:
            #. preferences (dictionary): The preferences dictionary.

        :Returns:
            #. flag (boolean): The check flag.
            #. message (string): The error message to raise.

        """
        return True, ""

    def reset_user(self):
        pref_loc = self.__default_dict()
        self.update_preferences(pref_loc)

    def set(self, key, value):
        pref_loc = self.preferences
        if key in pref_loc:
            pref_loc[key] = value
        else:
            logger.error('Can not set preference key %s for user %s' % (key, self.chat_id))
        self.update_preferences(pref_loc)

    def load(self):
        pref_loc = self.preferences
        self.__load_or_create(True)
        return self.__is_updated(pref_loc)

    def set_preferences(self, preferences=None):
        """
        Set preferences and update preferences file.

        :Parameters:
            #. preferences (dictionary): The preferences dictionary.
        """
        if preferences is None:
            preferences = self.__preferences
        flag, m = self.check_preferences(preferences)
        assert flag, m
        assert isinstance(preferences, dict), "Preferences must be a dictionary"
        # try dumping to temp file first
        self.__preferences = preferences
        # try:
        #     self.__dump_file(temp=True)
        # except Exception as e:
        #     logger.error("Unable to dump temporary preferences file (%s)" % e)
        # dump to file
        try:
            self.__dump_file(temp=False)
        except Exception as e:
            logger.error("Unable to dump preferences file (%s). "
                         "Preferences file can be corrupt, but in memory stored preferences are "
                         "still available using and accessible using preferences property." % e)
            # set preferences

    def update_preferences(self, preferences):
        """
        Update preferences and update preferences file.

        :Parameters:
            #. preferences (dictionary): The preferences dictionary.
        """
        flag, m = self.check_preferences(preferences)
        assert flag, m
        assert isinstance(preferences, dict), "Preferences must be a dictionary"
        new_preferences = self.preferences
        new_preferences.update(preferences)
        self.__preferences = new_preferences
        # set new preferences
        # self.set_preferences(new_preferences)
