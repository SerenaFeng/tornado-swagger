import json

import tornado.ioloop
from tornado.web import RequestHandler, HTTPError
from tornado_swagger import swagger

DEFAULT_REPRESENTATION = "application/json"
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

swagger.docs()

@swagger.model
class Details:
    def __init__(self, details=None):
        self.details = details

@swagger.model
class Item:
    """
        @descriptin:
            This is an example of a model class that has parameters in its constructor
            and the fields in the swagger spec are derived from the parameters to __init__.
        @notes:
            In this case we would have _id, name as required parameters and details as optional parameter.
        @property details: Item decription
        @ptype details: L{Details}
    """
    def __init__(self, _id, name, details=None):
        self._id = _id
        self.name = name
        self.details = details

items = {}

class GenericApiHandler(RequestHandler):
    """
    The purpose of this class is to take benefit of inheritance and prepare
    a set of common functions for
    the handlers
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        pass

    def prepare(self):
        if not (self.request.method == "GET" or self.request.method == "DELETE"):
            if self.request.headers.get("Content-Type") is not None:
                if self.request.headers["Content-Type"].startswith(DEFAULT_REPRESENTATION):
                    try:
                        self.json_args = json.loads(self.request.body)
                    except (ValueError, KeyError, TypeError) as error:
                        raise HTTPError(HTTP_BAD_REQUEST,
                                        "Bad Json format [{}]".
                                        format(error))
                else:
                    self.json_args = None

    def finish_request(self, json_object):
        self.write(json.dumps(json_object))
        self.set_header("Content-Type", DEFAULT_REPRESENTATION)
        self.finish()

class Pod1Handler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self):
        """
            @param body: create test results for a pod.
            @type body: L{Item}
            @return 200: pod is created.
            @raise 400: invalid input
        """
        id = self.json_args.get('_id')
        items[id] = self.json_args
        self.finish_request(items[id])

    @swagger.operation(nickname='list')
    def get(self):
        """
           @rtype: L{Item}
        """
        self.finish_request(items)

    def options(self):
        """
        I'm not visible in the swagger docs
        """
        self.finish_request("I'm invisible in the swagger docs")

class PodHandler(GenericApiHandler):
    @swagger.operation(nickname='get')
    def get(self, pod_id):
        """
            @rtype: L{Item}
            @description: get pod's test results
            @notes:
                get a pod test results,

                This will be added to the Implementation Notes.It lets you put very long text in your api.
        """
        self.finish_request(items[pod_id])

    @swagger.operation(nickname='delete')
    def delete(self, pod_id):
        """
            @description: delete pod by pod_id
            @notes:
                delete test results of a pod

                This will be added to the Implementation Notes.It lets you put very long text in your api.
        """
        del items[pod_id]
        self.finish_request("success")

class ProjectHandler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self, project, case=''):
        """
        @return 200: case is created
        """
        print("ProjectHandler.post: %s -- %s -- %s" % (project, case, self.request.full_url()))
        fs = open("/home/swagger/tornado-rest-swagger/%s/%s" % (project, case), "wb")
        fs.write(self.request.body)
        self.write("success")

def make_app():
    return swagger.Application([
        (r"/pods", Pod1Handler),
        (r"/pods/([^/]+)", PodHandler),
        (r"/projects/([^/]+)/cases/([^/]+)", ProjectHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(711)
    tornado.ioloop.IOLoop.current().start()
