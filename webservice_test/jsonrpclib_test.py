import jsonrpclib

HOST = 'localhost'
PORT = 8069
DB = 'odoo10'
USER = 'dianacarolinarojas@gmail.com'
PASS = 'admin'

# server proxy object
url = "http://%s:%s/jsonrpc" % (HOST, PORT)
server = jsonrpclib.Server(url)

# log in the given database
uid = server.call(service="common", method="login", args=[DB, USER, PASS])

# helper function for invoking model methods
def invoke(model, method, *args):
    args = [DB, uid, PASS, model, method] + list(args)
    return server.call(service="object", method="execute", args=args)

# create a new note
args = {'name': 'My session json rpclib','course_id' : 3,}
note_id = invoke('openacademy.session', 'create', args)