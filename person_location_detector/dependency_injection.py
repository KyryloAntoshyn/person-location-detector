from dependency_injector import containers, providers
import services


class DependencyInjectionContainer(containers.DeclarativeContainer):
    """
    Dependency injection container class.
    """
    configuration_provider = providers.Configuration()
    settings_service_provider = providers.Singleton(services.SettingsService)
