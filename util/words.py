
import os
from random import choice

class Words:

    def __init__(self, words_dir="words"):
        self.__words = {}
        self.__groups = {}
        for dir, dirs, files in os.walk(words_dir):
            name = dir.rpartition('/')[2]
            for fd in dirs:
                self.__groups[fd] = []
            for fn in files:
                self.__groups[name].append(fn)
                fp = os.path.join(dir, fn)
                with open(fp) as fi:
                    self.__words[fn] = [w.strip() for w in fi]

    def get_words(self, type=None):
        if type is not None:
            return self.__words[type]
        return self.__words[choice(self.__groups['general'])]
