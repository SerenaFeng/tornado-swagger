import json

import tornado.ioloop
from tornado.web import RequestHandler, HTTPError
from tornado_swagger import swagger

DEFAULT_REPRESENTATION = "application/json"
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

swagger.docs()


@swagger.model()
class PropertySubclass:
    def __init__(self, sub_property=None):
        self.sub_property = sub_property


@swagger.model()
class Item:
    """
        @description:
            This is an example of a model class that has parameters in its constructor
            and the fields in the swagger spec are derived from the parameters to __init__.
        @notes:
            In this case we would have property1, name as required parameters and property3 as optional parameter.
        @property property3: Item description
        @ptype property3: L{PropertySubclass}
        @ptype property4: C{list} of L{PropertySubclass}
    """
    def __init__(self, property1, property2=None, property3=None, property4=None):
        self.property1 = property1
        self.property2 = property2
        self.property3 = property3
        self.property4 = property4

    def format_http(self):
        return {
            "property1": self.property1,
            "property2": self.property2,
            "property3": self.property3,
            "property4": self.property4,
        }

    @staticmethod
    def item_from_dict(item_dict):

        if item_dict is None:
            return None

        t = Item(None)
        t.property1 = item_dict.get('property1')
        t.property2 = item_dict.get('property2')
        t.property3 = item_dict.get('property3')
        t.property4 = item_dict.get('property4')

        return t

    @classmethod
    def test_classmethod(cls):
        pass


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


class ItemNoParamHandler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self):
        """
            @param body: create a item.
            @type body: L{Item}
            @in body: body
            @return 200: item is created.
            @raise 400: invalid input
        """
        property1 = self.json_args.get('property1')
        item = Item.item_from_dict(self.json_args)
        items[property1] = item
        Item.test_classmethod()
        self.finish_request(item.format_http())

    @swagger.operation(nickname='list')
    def get(self):
        """
           @rtype: L{Item}
        """
        res = []
        for key, value in items.iteritems():
            res.append(value.format_http())
        self.finish_request(res)

    def options(self):
        """
        I'm not visible in the swagger docs
        """
        self.finish_request("I'm invisible in the swagger docs")


class ItemHandler(GenericApiHandler):
    @swagger.operation(nickname='get')
    def get(self, arg):
        """
            @rtype: L{Item}
            @description: get information of a item
            @notes:
                get a item,

                This will be added to the Implementation Notes.It lets you put very long text in your api.
        """
        self.finish_request(items[arg].format_http())

    @swagger.operation(nickname='delete')
    def delete(self, arg):
        """
            @description: delete a item
            @notes:
                delete a item in items

                This will be added to the Implementation Notes.It lets you put very long text in your api.
        """
        del items[arg]
        self.finish_request("success")


class ItemOptionParamHandler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self, arg1, arg2=''):
        """
        @return 200: case is created
        """
        print("ProjectHandler.post: %s -- %s -- %s" % (arg1, arg2, self.request.full_url()))
        fs = open("/home/swagger/tornado-rest-swagger/%s/%s" % (arg1, arg2), "wb")
        fs.write(self.request.body)
        self.write("success")


class ItemQueryHandler(GenericApiHandler):
    @swagger.operation(nickname='query')
    def get(self):
        """
           @param property1:
           @type property1: L{string}
           @in property1: query
           @required property1: False

           @param property2:
           @type property2: L{string}
           @in property2: query
           @required property2: True
           @rtype: L{Item}
           @notes: GET /item?property1=1&property2=1
        """
        property1 = self.get_query_argument("property1", None)
        property2 = self.get_query_argument("property2", None)

        res = []
        if property1 is None:
            for key, value in items.iteritems():
                if property2 is None:
                    res.append(value.format_http())
                elif value.property2 == property2:
                    res.append(value.format_http())
        elif items.has_key(property1):
            if items.get(property1).property2 == property2:
                res.append(items.get(property1).format_http())

        self.finish_request(res)


def make_app():
    return swagger.Application([
        (r"/item", ItemQueryHandler),
        (r"/items", ItemNoParamHandler),
        (r"/items/([^/]+)", ItemHandler),
        (r"/items/([^/]+)/cases/([^/]+)", ItemOptionParamHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(7111)
    tornado.ioloop.IOLoop.current().start()
