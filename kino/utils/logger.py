import datetime
import logging
import os


class Logger(object):
    class __Logger:
        def __init__(self):
            self._logger = logging.getLogger("crumbs")
            self._logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s"
            )

            now = datetime.datetime.now()

            dirname = "./log/activity/" + now.strftime("%Y-%m-%d")
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            fileHandler = logging.FileHandler(
                dirname + "/Kino_" + now.strftime("%Y-%m-%d %H:%M") + ".log"
            )
            streamHandler = logging.StreamHandler()

            fileHandler.setFormatter(formatter)
            streamHandler.setFormatter(formatter)

            self._logger.addHandler(fileHandler)
            self._logger.addHandler(streamHandler)

    instance = None

    def __init__(self):
        if not Logger.instance:
            Logger.instance = Logger.__Logger()

    def get_logger(self):
        return self.instance._logger


class MessageLogger(object):
    class __Logger:
        def __init__(self):
            self._logger = logging.getLogger("message")
            self._logger.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s > %(message)s")

            now = datetime.datetime.now()

            dirname = "./log/message"
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            fileHandler = logging.FileHandler(
                dirname + "/" + now.strftime("%Y-%m-%d") + ".log"
            )

            fileHandler.setFormatter(formatter)
            self._logger.addHandler(fileHandler)

    instance = None

    def __init__(self):
        if not MessageLogger.instance:
            MessageLogger.instance = MessageLogger.__Logger()

    def get_logger(self):
        return self.instance._logger


class DataLogger(object):
    class __Logger:
        def __init__(self, data_name):
            print("data logger " + data_name)
            self._logger = logging.getLogger(data_name)
            self._logger.setLevel(logging.INFO)

            dirname = "./log/data"
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            fileHandler = logging.FileHandler(dirname + f"/{data_name}.log")

            formatter = logging.Formatter("%(asctime)s > %(message)s")
            fileHandler.setFormatter(formatter)

            self._logger.addHandler(fileHandler)

    instance = {}

    def __init__(self, data_name):
        self.data_name = data_name

        if data_name not in DataLogger.instance:
            DataLogger.instance[data_name] = DataLogger.__Logger(data_name)

    def get_logger(self):
        return self.instance[self.data_name]._logger
