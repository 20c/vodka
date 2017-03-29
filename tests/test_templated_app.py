import os.path
import unittest
import vodka.instance
import vodka.app

@vodka.app.register('templated_app_a')
class TemplatedAppA(vodka.app.TemplatedApplication):
    pass

@vodka.app.register('templated_app_b')
class TemplatedAppB(vodka.app.TemplatedApplication):
    pass

resources_dir = os.path.join(os.path.dirname(__file__), "resources", "test_templated_app")

def rsrc(name):
    return os.path.join(resources_dir, name)

class TestTemplatedApp(unittest.TestCase):

    def test_render(self):
        vodka.instance.instantiate({
            "apps" : {
                TemplatedAppA.handle : {
                    "enabled" : True,
                    "templates" : rsrc("a"),
                    "template_locations": [
                        rsrc("a2")
                    ]
                },
                TemplatedAppB.handle : {
                    "enabled" : True,
                    "templates" : rsrc("b")
                }
            }
        })

        inst= vodka.instance.get_instance(TemplatedAppA.handle)
        vodka.instance.ready()

        r = inst.render("base.html", {})
        self.assertEqual(r,u"Hello World!")

        r = inst.render("template_a.html", {})
        self.assertEqual(r,u"Hello Universe!")

        r = inst.render("template_b.html", {})
        self.assertEqual(r,u"Hello Infinity!")
