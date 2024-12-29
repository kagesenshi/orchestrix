import fastapi

router = fastapi.APIRouter()

@router.get("/tenants/{tenant_id}/clusters/")
def get_tenant_clusters(tenant_id: int) -> dict:
    # get clusters by tenant id
    return {}

@router.post("/tenants/{tenant_id}/clusters/")
def create_tenant_cluster(tenant_id: int, cluster: dict) -> dict:
    # create cluster for tenant
    return {}

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}")
def get_tenant_cluster(tenant_id: int, cluster_id: int) -> dict:
    # get cluster by tenant id and cluster id
    return {}

@router.put("/tenants/{tenant_id}/clusters/{cluster_id}")
def update_tenant_cluster(tenant_id: int, cluster_id: int, cluster: dict) -> dict:
    # update cluster by tenant id and cluster id
    return {}

@router.delete("/tenants/{tenant_id}/clusters/{cluster_id}")
def delete_tenant_cluster(tenant_id: int, cluster_id: int) -> dict:
    # delete cluster by tenant id and cluster id
    return {}

@router.get("/tenants/{tenant_id}/clusters/{cluster_id}/hosts")
def get_tenant_cluster_hosts(tenant_id: int, cluster_id: int) -> dict:
    # get hosts by tenant id and cluster id
    return {}

@router.post("/tenants/{tenant_id}/clusters/{cluster_id}/hosts/")
def assign_host_to_cluster(tenant_id: int, cluster_id: int) -> dict:
    # get hosts by tenant id and cluster id
    return {}

@router.delete("/tenants/{tenant_id}/clusters/{cluster_id}/hosts/{host_id}")
def remove_host_from_cluster(tenant_id: int, cluster_id: int, host_id: int) -> dict:
    return {}
