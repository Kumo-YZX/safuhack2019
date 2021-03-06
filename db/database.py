###
##
#database to record transactions.

#out put:print 'db/database.py: '

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('config', '../config.py')
from pymongo import MongoClient
import config

class dbbase(object):

    def __init__(self, 
                 address = config.dbaddress, 
                 port = config.dbport):
        self.mydb = MongoClient(address, port).safuhackdb
        print 'db/database.py: dbbase init done'


class transdb(dbbase):

    def __init__(self):
        dbbase.__init__(self)
        self.__trans = self.mydb.tranSet
        print 'db/database.py: transdb init done'
    
    def saveOne(self, tran_as_json):
        # need to check the format
        self.__trans.insert_one(tran_as_json)
        print 'db/database.py: save one transdb done'

    # def search

class scoredb(dbbase):
    
    def __init__(self):
        dbbase.__init__(self)
        self.__scores = self.mydb.scoreSet
        print 'db/database.py: scoredb init done'

    def saveOne(self, score_as_json):
        try:
            score_as_json['address']
            score_as_json['score']
        except KeyError:
            return 2
        self.__scores.insert_one(score_as_json)
        print 'db/database.py: scoredb save one done'
        return 1

    def queryOne(self, address_as_json):
        try:
            address_as_json['address']
        except KeyError:
            return 2
        res = self.__scores.find_one({"address":address_as_json["address"]})
        print 'db/database.py: query scoredb done'
        return res      #may be None!!

    def updateOne(self, score_as_json):
        try:
            score_as_json['address']
            score_as_json['score']
        except KeyError:
            return 2
        self.__scores.update_one({"address":score_as_json["address"]}, {'$set':{"score":score_as_json["score"]}})
        print 'db/database.py: scoredb update one done'
        return 1


class reportdb(dbbase):

    def __init__(self):
        dbbase.__init__(self)
        self.__reports = self.mydb.reportSet
        print 'db/database.py: reportdb init done'

    def saveOne(self, report_as_json):
        try:
            report_as_json['rep_addr']
            report_as_json['prove']
        except KeyError:
            return 2
        report_as_json['tag'] = 0
        self.__reports.insert_one(report_as_json)
        print 'db/database.py: save one report to database done'
        return 1

    def readAddr(self, address_as_json):
        try:
            address_as_json['rep_addr']
        except KeyError:
            return 2
        res = list(self.__reports.find({"rep_addr":address_as_json['rep_addr']}))
        if (res is not None) and (not ('do_mark' in address_as_json)):
            self.__reports.update_many({"rep_addr":address_as_json['rep_addr']}, {'$set':{'tag':1}})
            print 'db/database.py: read report done with tag set to 1'
            return res
        else:
            return res #may be None!!

    def searchAddr(self, address_as_json):
        try:
            address_as_json['rep_addr']
        except KeyError:
            return 2
        res = list(self.__reports.find({"rep_addr":address_as_json['rep_addr']}))
        print 'db/database.py: search report done'
        return res

    def unread(self):
        """Search for all unread reports
        """
        res = list(self.__reports.find({'tag':0}))
        self.__reports.update_many({'tag':0}, {'$set':{'tag':1}})
        print 'db/database.py: search for unread reps done'
        return res


# class dbtest(object):

#     def __init__(self):
#         print 'db/database.py: '

#     def scoreSaveOne(self, parameter):
#         obj = scoredb
#         obj.saveOne(parameter)
    
#     def scoreQueryOne(self, parameter):
#         obj = scoredb
#         obj.queryOne(parameter)

if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 3:
        print 'db/database.py: test error: parameters required!!'
    else:
        if sys.argv[1] == 'scoresave':
            obj = scoredb()
            print obj.saveOne(json.loads(sys.argv[2]))
        elif sys.argv[1] == 'scorequery':
            obj = scoredb()
            print obj.queryOne(json.loads(sys.argv[2]))

        elif sys.argv[1] == 'repsave':
            obj = reportdb()
            print obj.saveOne(json.loads(sys.argv[2]))
        elif sys.argv[1] == 'repread':
            obj = reportdb()
            print obj.readAddr(json.loads(sys.argv[2]))
        elif sys.argv[1] == 'repsearch':
            obj = reportdb() 
            print obj.searchAddr(json.loads(sys.argv[2]))
        elif sys.argv[1] == 'repunread':
            obj = reportdb() 
            print obj.unread()
        else:
            print 'db/database.py: wrong format'


