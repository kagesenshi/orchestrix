import fastapi

router = fastapi.APIRouter()

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}/available_services/")
def get_available_services(tenant_id: int, cluster_id: str) -> dict:
    # get list of available services that can be installed
    return {}

@router.post("/tenants/{tenant_id}/clusters/{cluster_id}/services/")
def install_service(tenant_id: int, cluster_id: str, service: dict) -> dict:
    # install service on cluster
    return {}

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}/services/{service_id}")
def get_service(tenant_id: int, cluster_id: str, service_id: int) -> dict:
    # get service by id
    return {}

@router.delete("/tenants/{tenant_id}/clusters/{cluster_id}/services/{service_id}")
def uninstall_service(tenant_id: int, cluster_id: str, service_id: int) -> dict:
    # uninstall service from cluster
    return {}

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}/services/")
def get_services(tenant_id: int, cluster_id: str) -> dict:
    # get list of services installed on cluster
    return {}

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}/services/{service_id}/configuration/")
def get_service_configuration(tenant_id: int, cluster_id: str, service_id: int) -> dict:
    # get service configuration
    return {}

@router.put("/tenants/{tenant_id}/clusters/{cluster_id}/services/{service_id}/configuration/{config_key}")
def update_service_configuration(tenant_id: int, cluster_id: str, service_id: int, config_key: str, config_value: str) -> dict:
    # update service configuration
    return {}

@router.delete("/tenants/{tenant_id}/clusters/{cluster_id}/services/{service_id}/configuration/{config_key}")
def delete_service_configuration(tenant_id: int, cluster_id: str, service_id: int, config_key: str) -> dict:
    # delete service configuration / reset to default
    return {}