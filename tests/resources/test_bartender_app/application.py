"""
application for test_bartender will be loaded from
here
"""

import vodka.app


@vodka.app.register("test_bartender_app")
class Application(vodka.app.Application):
    setup_done = False

    def setup(self):
        self.setup_done = True
