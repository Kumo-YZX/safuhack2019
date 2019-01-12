def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('database', '../db/database.py')

import database

class parseMsg(object):

    def __init__(self, user, word):
        self.__user = user
        self.__word = word
        print 'parse/parse.py: parseMsg obj init done'

    def replyWord(self):
        self.judgeType()
        if self.__type == 2:
            rep = self.queryScore(self.__word[2:])
        elif self.__type == 3:
            rep = self.reportAddress(self.__word[2:45], self.__word[46:])
        else:
            rep = 'Wrong Format'
        return rep

    def judgeType(self):
        if str.upper(self.__word[0:2]) == 'RE':
            self.__type = 2
        elif str.upper(self.__word[0:2]) == 'QU':
            self.__type = 3
        else:
            self.__type = 0
        
    def queryScore(self, address):
        scoreObj = database.scoredb()
        score_query_res = scoreObj.queryOne({"address":address})
        if score_query_res is None:
            res_msg = 'Address: [{}]\nSorry We are not able to provide score about this address.'
        else:
            res_msg = 'Address: [{}]\nOur Score:[{}]'.format(score_query_res["address"],
                                                            score_query_res["score"])
        return res_msg

    def reportAddress(self, address, msg):
        return 'report function not avilable now.'