from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, Field

from app.application.command.network import (
    NetworkAttachCommand,
    NetworkCreateCommand,
    NetworkSearchQuery,
)
from app.domain.models import Network, NetworkHostState, NetworkSyncStatus


class NetworkSearchQueryParam(BaseModel):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=50)

    def to_query(self) -> NetworkSearchQuery:
        return NetworkSearchQuery(page=self.page, size=self.size)


class NetworkCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    driver: str = Field(default="bridge", min_length=1, max_length=50)
    options: dict[str, str] = Field(default_factory=dict)

    def to_command(self) -> NetworkCreateCommand:
        return NetworkCreateCommand(
            name=self.name, driver=self.driver, options=self.options
        )


class NetworkAttachRequest(BaseModel):
    workload_id: int
    alias: str | None = Field(default=None, min_length=1, max_length=255)

    def to_command(self, network_id: int) -> NetworkAttachCommand:
        return NetworkAttachCommand(
            workload_id=self.workload_id, network_id=network_id, alias=self.alias
        )


class NetworkResponse(BaseModel):
    id: int
    name: str
    driver: str
    options: dict[str, str] = Field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, network: Network) -> NetworkResponse:
        return cls.model_construct(
            id=network.pk,
            name=network.name,
            driver=network.driver,
            options=network.options,
            created_at=network.created_at,
        )


class NetworkListResponse(BaseModel):
    networks: list[NetworkResponse]

    @classmethod
    def from_result(cls, networks: list[Network]) -> NetworkListResponse:
        return cls(networks=[NetworkResponse.from_domain(n) for n in networks])


class NetworkHostStateResponse(BaseModel):
    id: int
    network_id: int
    host_id: int
    status: NetworkSyncStatus
    error_message: str | None = None
    synced_at: datetime | None = None

    @classmethod
    def from_domain(cls, state: NetworkHostState) -> NetworkHostStateResponse:
        return cls.model_construct(
            id=state.pk,
            network_id=state.network_id,
            host_id=state.host_id,
            status=state.status,
            error_message=state.error_message,
            synced_at=state.synced_at,
        )


class NetworkHostStateListResponse(BaseModel):
    states: list[NetworkHostStateResponse]

    @classmethod
    def from_result(
        cls, states: list[NetworkHostState]
    ) -> NetworkHostStateListResponse:
        return cls(states=[NetworkHostStateResponse.from_domain(s) for s in states])
