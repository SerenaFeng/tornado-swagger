# tornado-swagger

## What is tornado-swagger?
tornado is a wrapper for tornado which enables swagger-ui support.

In essense, you just need to wrap the Api instance and add a few python decorators to get full swagger support.

## How to:
Install:

```
python setup.py install
```
(This installs tornado and epydoc as well)


And in your program, where you'd usually just use tornado, add just a little bit of sauce and get a swagger spec out.


```python
from tornado.web import RequestHandler, HTTPError
from tornado_swagger import swagger

swagger.docs()

# You may decorate your operation with @swagger.operation and use docs to inform information
class Pod1Handler(GenericApiHandler):
    @swagger.operation(nickname='create')
    def post(self):
        """
            @param body: create test results for a pod.
            @type body: L{Item}
            @return 200: pod is created.
            @raise 400: invalid input
        """

# Operations not decorated with @swagger.operation do not get added to the swagger docs

class Pod1Handler(GenericApiHandler):
    def options(self):
        """
        I'm not visible in the swagger docs
        """
        pass


# Then you use swagger.Application instead of tornado.web.Application
# and do other operations as usual

def make_app():
    return swagger.Application([
        (r"/pods", Pod1Handler),
        (r"/pods/([^/]+)", PodHandler),
        (r"/projects/([^/]+)/cases/([^/]+)", ProjectHandler),
    ])

# You define models like this:
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
    def __init__(self, _id, name=None):
        self._id = _id
        self.name = name

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "_id",
            ],
            "properties": [
                "_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                    "default": null
                }
            ]
        }
    }

# If you declare an __init__ method with meaningful arguments
# then those args could be used to deduce the swagger model fields.
# just as shown above

# if you declare an @property in docs, this property name will also be used to deduce the swagger model fields
class Item:
    """
        @property details: Item description
    """
    def __init__(self, _id, name):
        self._id = _id
        self.name = name

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "_id",
            ],
            "properties": [
                "_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                }
                "details": {
                    "type": "string"
                }
            ]
        }
    }

# if you declare an argument with @ptype, the type of this argument will be specified rather than the default 'string'
class Item:
    """
        @ptype details: L{Details}
    """
    def __init__(self, _id, name, details=None):
        self._id = _id
        self.name = name
        self.details = details

# Swagger json:
    "models": {
        "Item": {
            "description": "A description...",
            "id": "Item",
            "required": [
                "_id",
            ],
            "properties": [
                "_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "details": {
                    "type": "Details"
                    "default": null
                }
            ]
        }
    }
```

# Running and testing

Now run your tornado app

```
python basic.py
```

And visit:

```
curl http://localhost:711/swagger/spec
```

access to web
```
http://localhost:711/swagger/spec.html
```

# Passing more metadata to swagger
customized arguments used in creating the 'swagger.docs' object will be supported later
