###
##
# main server process

import tornado.ioloop
import tornado.web
import config
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from wx import reply2, receive


class testHandler(tornado.web.RequestHandler):

    def get(self):
        print 'server.py: PageHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"ok", "method":"get"})

    def post(self):
        print 'server.py: PageHandler: POST request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"ok", "method":"post"})

class wxHandler(tornado.web.RequestHandler):

    def get(self):
        print 'server.py: Info: WxHandler: GET request from {}'.format(self.request.remote_ip)

        requestDict = self.request.query

        try:
            paraList = [config.token, requestDict['timestamp'], requestDict['nonce']]
            sign = requestDict['signature']
            echo = requestDict['echostr']
            paraList.sort()

            import hashlib
            sha1 = hashlib.sha1()
            map(sha1.update, paraList)
            hashCode = sha1.hexdigest()
            print 'hashCode, signature:' + hashCode, sign

            if hashCode == sign:
                self.write(echo)

            else:
                self.write('server: Error: verify failed')
        except KeyError:
            self.write('server: Error: some query parameter missing')

    def post(self):
        print 'server.py: Info: WxHandler: POST request from {}'.format(self.request.remote_ip)
        token = config.token
        encodingKey = config.encodingkey
        appid = config.appid
        encodingkey = config.encodingkey
        decryptObj = WXBizMsgCrypt(token, encodingKey, appid)
        try:
            stamp = self.get_query_arguments("timestamp")[0]
            nonce = self.get_query_arguments("nonce")[0]
            msgSign = self.get_query_arguments("msg_signature")[0]

            decStatus, wxData = decryptObj.DecryptMsg(self.request.body, msgSign, stamp, nonce)
            if decStatus:
                print 'server.py: Error: decrypt fail'
                self.write('server: Error: Decrypt fail')
            else:
                print 'server.py: Info: wxData:', wxData
                recData = receive.parse_xml(wxData)
                from parse import parse
                if isinstance(recData, receive.Msg) and recData.MsgType == 'text':
                    toUser = recData.FromUserName
                    fromUser = recData.ToUserName
                    word = recData.Content

                    parseObj = parse.parseMsg(toUser, word)
                    content = parseObj.replyWord()
                else:
                    print 'server.py: Error: wrong format'
                    toUser = recData.FromUserName
                    fromUser = recData.ToUserName
                    content = 'The format is wrong.'

                encryptObj = WXBizMsgCrypt(token, encodingkey, appid)
                encStatus, replyData = encryptObj.EncryptMsg(reply2.TextMsg(toUser, fromUser, content), nonce, stamp)
                if encStatus:
                    self.write('server: Error: Encrypt fail:' + str(encStatus))
                else:
                    self.write(replyData)
        except IndexError:
            self.write('server: error: some query parameter missing')
            
class scoreApiHandler(tornado.web.RequestHandler):

    def get(self):
        print 'server.py: Info: scoreApiHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"method not supported", "method":"post"})
    
    def post(self):
        import json
        user_ip = self.request.remote_ip
        
        request_account_address = json.loads(self.request.body)["address"]
        print 'server.py: Info: scoreApiHandler: POST request from {} with address [{}]'.format(user_ip, 
                                                                                request_account_address)
        from db import database
        scoreObj = database.scoredb()
        score_query_res = scoreObj.queryOne({"address":request_account_address})
        if score_query_res is None:
            self.write({"httpstatus":200, 
                        "msg":"address not found",
                        "method":"post"})
        else:
            self.write({"httpstatus":200, 
                        "msg":"query done",
                        "method":"post",
                        "address":score_query_res["address"],
                        "score":score_query_res["score"]})

class reportApiHandler(tornado.web.RequestHandler):

    def get(self):
        print 'server.py: Info: reportApiHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"method not supported", "method":"get"})
    
    def post(self):
        self.write({"httpstatus":200, "msg":"method not supported", "method":"post"})
        

class updateApiHandler(tornado.web.RequestHandler):

    def get(self):
        print 'server.py: Info: updateApiHandler: GET request from {}'.format(self.request.remote_ip)
        self.write({"httpstatus":200, "msg":"method not supported", "method":"get"})
    
    def post(self):
        self.write({"httpstatus":200, "msg":"method not supported", "method":"post"})

def startApp():
    return tornado.web.Application([
        (config.testHandlerUrl, testHandler),
        (config.wxHandlerUrl, wxHandler),
        (config.scoreApiHandlerUrl, scoreApiHandler),
        (config.reportApiHandlerUrl, reportApiHandler),
        (config.updateApiHandlerUrl, updateApiHandler)
    ])

if __name__ == "__main__":
    app = startApp()
    app.listen(address = "0.0.0.0", port = config.serverListenPort)
    tornado.ioloop.IOLoop.current().start()
