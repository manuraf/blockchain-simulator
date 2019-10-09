import json
import cherrypy
from cherrypy.lib import static
import os
import os.path

from Service import Service

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)


@cherrypy.expose
class ExperimentalWs(object):

    def __init__(self):
        self.service = Service()

    def GET(self, *uri, **params):
        if len(uri) == 0:
            return ""

        uri_object = uri[0]
        if uri_object != 'check' and uri_object != 'execute':
            cherrypy.HTTPError(500, "uri error")

        if uri_object == 'experiments':
            id_expe = uri[1]
            result = self.service.get_experiments(id_expe)
            return json.dumps({'data': result})

        if uri_object == 'check':
            id_expe = uri[1]
            result = self.service.get_experiment(id_expe)
            if result is None:
                return json.dumps({'data': result})
            else:
                return json.dumps({'data': result})

        if uri_object == 'execute':
            n_expe = uri[1]
            settings = {"node": params["node"], "iteration": params["iteration"]}

            id = self.service.execute(int(n_expe), settings)
            return json.dumps({'id': id})

        if uri_object == 'gif':
            file = self.service.create_gif()
            path = os.path.join(absDir, file)
            return static.serve_file(path, 'image/gif',
                                     'attachment', os.path.basename(path))

        return json.dumps({'response': "OK"})

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.CORS.on': True

        }
    }
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(ExperimentalWs(), '/experimentals', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 9080})
    cherrypy.engine.start()
    cherrypy.engine.block()