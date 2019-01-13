# parse.py, receive words from wechat users and return replies.

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
            report_address, report_prove = (self.__word[2:]).split('PR')
            rep = self.reportAddress(report_address, report_prove)
        else:
            rep = 'Sorry, The service is not avilable now, we will repair it soon.'
        return rep

    def judgeType(self):
        if str.upper(self.__word[0:2]) == 'QU':
            self.__type = 2
        elif str.upper(self.__word[0:2]) == 'RE':
            self.__type = 3
        else:
            self.__type = 0
        
    def queryScore(self, address):
        # query for the score of the address.
        scoreObj = database.scoredb()
        score_query_res = scoreObj.queryOne({"address":address})
        if score_query_res is None:
            res_msg = 'Address: [{}]\nSorry We are not able to provide score about this address.'.format(address)
        else:
            res_msg = 'Address: [{}]\nScore: [{}]'.format(score_query_res["address"],
                                                            score_query_res["score"])
        return res_msg

    def reportAddress(self, address, msg):
        reportObj = database.reportdb()
        reportObj.saveOne({"rep_addr":address,
                           "prove":msg})
        print 'report of address:[{}] with prove msg [{}] done.'.format(address, msg)
        return 'Thank You for Your report about address [{}]!'.format(address)