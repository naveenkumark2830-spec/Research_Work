from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.state.session_state import SessionState
from app.simulation.hdfs.cluster import HDFSClusterConfig, HDFSClusterState
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.services.hdfs_service import HDFSService
from app.jarvis.action_validator import bytes_from_size

router = APIRouter()


def get_hdfs_service(db: DBSession = Depends(get_db)) -> HDFSService:
    session_repo = SQLAlchemySessionRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    return HDFSService(session_repo, event_repo)


class HDFSFileRequest(BaseModel):
    session_id: str
    path: str = Field(min_length=1)
    size: float = Field(gt=0)
    unit: str = "MB"
    user_id: Optional[str] = None


class HDFSFailureRequest(BaseModel):
    session_id: str
    node_id: str
    user_id: Optional[str] = None


class HDFSRecoveryRequest(BaseModel):
    session_id: str
    node_id: str
    user_id: Optional[str] = None


class WriteFileRequest(BaseModel):
    user_id: Optional[str] = None
    path: str = Field(..., json_schema_extra={"example": "input/data.csv"})
    size_bytes: int = Field(..., gt=0, json_schema_extra={"example": 524288000})


class ReadFileRequest(BaseModel):
    user_id: Optional[str] = None
    path: str = Field(..., json_schema_extra={"example": "input/data.csv"})


class CreateClusterRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    config: Optional[HDFSClusterConfig] = None


class UpdateConfigRequest(BaseModel):
    user_id: Optional[str] = None
    config: HDFSClusterConfig


class SetSpeedRequest(BaseModel):
    user_id: Optional[str] = None
    speed: float = Field(..., ge=0.1, le=10.0)


@router.post("/cluster", response_model=SessionState, status_code=201, summary="Create HDFS Cluster")
def create_cluster(
    request: CreateClusterRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or request.user_id
    return service.create_cluster(request.session_id, request.config, user_id=target_user_id)


@router.put("/sessions/{session_id}/config", response_model=SessionState, summary="Update HDFS Simulation Config")
def update_config(
    session_id: str,
    request: UpdateConfigRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or request.user_id
    return service.update_config(session_id, request.config, user_id=target_user_id)


@router.post("/sessions/{session_id}/speed", response_model=SessionState, summary="Set Simulation Speed")
def set_speed(
    session_id: str,
    request: SetSpeedRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or request.user_id
    return service.set_speed(session_id, request.speed, user_id=target_user_id)


@router.post("/sessions/{session_id}/write", response_model=SessionState, summary="Write File to HDFS")
def write_file(
    session_id: str,
    request: WriteFileRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or request.user_id
    return service.write_file(session_id, request.path, request.size_bytes, user_id=target_user_id)


@router.post("/sessions/{session_id}/read", summary="Read File from HDFS")
def read_file(
    session_id: str,
    request: ReadFileRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or request.user_id
    return service.read_file(session_id, request.path, user_id=target_user_id)


@router.post("/sessions/{session_id}/datanodes", response_model=SessionState, status_code=201, summary="Add DataNode")
def add_datanode(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.add_datanode(session_id, user_id=target_user_id)


@router.delete("/sessions/{session_id}/datanodes/{node_id}", response_model=SessionState, summary="Remove DataNode")
def remove_datanode(
    session_id: str,
    node_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.remove_datanode(session_id, node_id, user_id=target_user_id)


@router.post("/sessions/{session_id}/datanodes/{node_id}/fail", response_model=SessionState, summary="Fail DataNode")
@router.post("/sessions/{session_id}/datanodes/{node_id}/kill", response_model=SessionState, summary="Kill DataNode")
def kill_datanode(
    session_id: str,
    node_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.kill_datanode(session_id, node_id, user_id=target_user_id)


@router.post("/sessions/{session_id}/datanodes/{node_id}/recover", response_model=SessionState, summary="Recover DataNode")
def recover_datanode(
    session_id: str,
    node_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.recover_datanode(session_id, node_id, user_id=target_user_id)


@router.post("/sessions/{session_id}/recover", response_model=SessionState, summary="Recover Under-Replicated Blocks")
def recover_under_replicated_blocks(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.recover_under_replicated_blocks(session_id, user_id=target_user_id)


@router.post("/sessions/{session_id}/restart", response_model=SessionState, summary="Restart HDFS Simulation")
def restart_simulation(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.restart_simulation(session_id, user_id=target_user_id)


@router.get("/sessions/{session_id}/state", response_model=HDFSClusterState, summary="Get HDFS Cluster State")
def get_hdfs_cluster_state(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    target_user_id = x_user_id or user_id
    return service.get_hdfs_cluster_state(session_id, user_id=target_user_id)


# ---------------------------------------------------------
# Teddy Direct API Endpoints (Stages 8.3 - 8.6)
# ---------------------------------------------------------

@router.post("/file", summary="Teddy Write File API")
def write_hdfs_file(
    request: HDFSFileRequest,
    service: HDFSService = Depends(get_hdfs_service)
):
    size_bytes = bytes_from_size(request.size, request.unit)

    state = service.write_file(
        session_id=request.session_id,
        path=request.path,
        size_bytes=size_bytes,
        user_id=request.user_id,
    )

    return {
        "success": True,
        "action": "write_file",
        "session_id": request.session_id,
        "path": request.path,
        "size_bytes": size_bytes,
        "state": state,
    }


@router.get("/state/{session_id}", summary="Teddy Get HDFS State API")
def get_hdfs_state(
    session_id: str,
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    state = service.get_hdfs_cluster_state(
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "session_id": session_id,
        "state": state,
    }


@router.post("/failure", summary="Teddy Fail DataNode API")
def fail_datanode(
    request: HDFSFailureRequest,
    service: HDFSService = Depends(get_hdfs_service)
):
    state = service.kill_datanode(
        session_id=request.session_id,
        node_id=request.node_id,
        user_id=request.user_id,
    )

    return {
        "success": True,
        "action": "kill_datanode",
        "session_id": request.session_id,
        "node_id": request.node_id,
        "state": state,
    }


@router.post("/recovery", summary="Teddy Recover DataNode API")
def recover_datanode(
    request: HDFSRecoveryRequest,
    service: HDFSService = Depends(get_hdfs_service)
):
    state = service.recover_datanode(
        session_id=request.session_id,
        node_id=request.node_id,
        user_id=request.user_id,
    )

    return {
        "success": True,
        "action": "recover_datanode",
        "session_id": request.session_id,
        "node_id": request.node_id,
        "state": state,
    }


@router.post("/recovery/under-replicated", summary="Teddy Recover Under-Replicated Blocks API")
def recover_under_replicated(
    session_id: str,
    user_id: Optional[str] = None,
    service: HDFSService = Depends(get_hdfs_service)
):
    state = service.recover_under_replicated_blocks(
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "action": "recover_under_replicated_blocks",
        "session_id": session_id,
        "state": state,
    }
