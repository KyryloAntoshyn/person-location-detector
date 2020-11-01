import os
import sys
from configuration.container import Container


def main():
    """
    Application entry point. Creates dependency injection container, initializes and starts application.
    """
    container = Container()
    container.configuration_provider.from_ini(os.path.join("configuration", "configuration.ini"))
    container.wire(modules=[sys.modules[__name__]])

    container.initialization_service_provider().initialize_and_start_application()


if __name__ == "__main__":
    main()
