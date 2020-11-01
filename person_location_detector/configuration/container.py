from dependency_injector import containers, providers
from services.initialization_service import InitializationService


class Container(containers.DeclarativeContainer):
    configuration_provider = providers.Configuration()

    initialization_service_provider = providers.Singleton(InitializationService)
