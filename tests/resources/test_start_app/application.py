"""
application for test_start will be loaded from
here
"""

import vodka.app


@vodka.app.register("test_start_app")
class Application(vodka.app.Application):
    setup_done = False

    def setup(self):
        self.setup_done = True


@vodka.app.register("test_start_app_inactive")
class InactiveApplication(Application):
    pass


@vodka.app.register("test_start_app_skipped")
class SkippedApplication(Application):
    pass
