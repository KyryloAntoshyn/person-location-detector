import services
from dependency_injector import containers, providers


class DependencyInjectionContainer(containers.DeclarativeContainer):
    """
    Dependency injection container class.
    """
    configuration_provider = providers.Configuration()
    camera_service_provider = providers.Singleton(services.CameraService)
    detection_service_provider = providers.Singleton(services.PersonLocationDetectionService)
