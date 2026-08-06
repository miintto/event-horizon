from dataclasses import replace
from datetime import UTC, datetime, timedelta

from app.application.command.deployment import (
    ClaimResult,
    DeploymentClaimCommand,
    DeploymentCreateCommand,
    DeploymentReportCommand,
    DeploymentSearchQuery,
)
from app.application.ports.repository import (
    ContainerRepository,
    DeploymentRepository,
    HostRepository,
    SecretRepository,
    WorkloadRepository,
    WorkloadRevisionRepository,
)
from app.application.ports.security import SecretCipher
from app.application.ports.usecase import DeploymentUseCase
from app.domain.exceptions import (
    DeploymentInProgressException,
    DeploymentNotFoundException,
    HostNotFoundException,
    RevisionRequiredException,
    SecretNotFoundException,
    WorkloadNotFoundException,
    WorkloadRevisionNotFoundException,
)
from app.domain.models import (
    Container,
    ContainerSpec,
    ContainerState,
    Deployment,
    DeploymentStatus,
    EnvVar,
    Workload,
    WorkloadRevision,
)
from app.infrastructure.transaction import transactional


class DeploymentService(DeploymentUseCase):
    def __init__(
        self,
        container_repository: ContainerRepository,
        deployment_repository: DeploymentRepository,
        host_repository: HostRepository,
        secret_repository: SecretRepository,
        workload_repository: WorkloadRepository,
        workload_revision_repository: WorkloadRevisionRepository,
        secret_cipher: SecretCipher,
        timeout_secs: int,
    ):
        self._container_repository = container_repository
        self._deployment_repository = deployment_repository
        self._host_repository = host_repository
        self._secret_repository = secret_repository
        self._workload_repository = workload_repository
        self._workload_revision_repository = workload_revision_repository
        self._secret_cipher = secret_cipher
        self._timeout_secs = timeout_secs

    @transactional
    async def get_deployment(self, deployment_id: int) -> Deployment:
        deployment = await self._deployment_repository.find_by_id(deployment_id)
        if not deployment:
            raise DeploymentNotFoundException
        return deployment

    @transactional
    async def get_deployments(self, query: DeploymentSearchQuery) -> list[Deployment]:
        return await self._deployment_repository.find_all(
            host_id=query.host_id, workload_id=query.workload_id
        )

    @transactional
    async def create_deployment(self, command: DeploymentCreateCommand) -> Deployment:
        workload = await self._workload_repository.find_by_id(command.workload_id)
        if not workload:
            raise WorkloadNotFoundException
        elif not await self._host_repository.find_by_id(command.host_id):
            raise HostNotFoundException
        elif await self._deployment_repository.find_active(workload.pk):
            raise DeploymentInProgressException

        revision = await self._find_revision(workload, command.revision_id)

        return await self._deployment_repository.save(
            Deployment(
                host_id=command.host_id,
                workload_id=workload.pk,
                revision_id=revision.pk,
                status=DeploymentStatus.PENDING,
            )
        )

    @transactional
    async def claim(self, command: DeploymentClaimCommand) -> ClaimResult | None:
        host = await self._host_repository.find_by_agent_uuid(command.agent_uuid)
        if not host:
            raise HostNotFoundException

        await self._deployment_repository.update_status_to_failed(
            active_before=datetime.now(UTC) - timedelta(seconds=self._timeout_secs),
            error_message="Deployment timed out",
        )

        deployment = await self._deployment_repository.find_oldest_pending(host.pk)
        if not deployment:
            return None

        workload = await self._workload_repository.find_by_id(deployment.workload_id)
        revision = await self._workload_revision_repository.find_by_id(
            deployment.revision_id
        )
        if not workload or not revision:
            return await self._abort(deployment, "Workload or revision is gone")

        try:
            spec = await self._resolve_spec(revision.spec)
        except SecretNotFoundException as exc:
            return await self._abort(deployment, exc.detail)

        deployment.status = DeploymentStatus.RUNNING
        deployment.claimed_at = datetime.now(UTC)
        await self._deployment_repository.save(deployment)

        return ClaimResult(
            deployment_id=deployment.pk,
            container_name=self._container_name(workload, revision, deployment),
            image=revision.image,
            spec=spec,
            cpu_limit=revision.cpu_limit,
            memory_limit=revision.memory_limit,
            labels={
                "horizon.workload_id": str(deployment.workload_id),
                "horizon.revision_id": str(deployment.revision_id),
                "horizon.deployment_id": str(deployment.pk),
            },
            previous_docker_ids=await self._container_repository.find_docker_ids_alive(
                workload_id=deployment.workload_id, host_id=host.pk
            ),
        )

    @transactional
    async def report(self, command: DeploymentReportCommand) -> Deployment:
        host = await self._host_repository.find_by_agent_uuid(command.agent_uuid)
        if not host:
            raise HostNotFoundException

        deployment = await self._deployment_repository.find_by_id(command.deployment_id)
        if not deployment or deployment.host_id != host.pk:
            raise DeploymentNotFoundException
        elif deployment.status is not DeploymentStatus.RUNNING:
            return deployment
        elif command.status is DeploymentStatus.SUCCEEDED:
            deployment.container_id = await self._link_container(deployment, command)
            await self._container_repository.mark_exited(
                host.pk, command.removed_docker_ids
            )

        deployment.status = command.status
        deployment.error_message = command.error_message
        deployment.finished_at = datetime.now(UTC)
        return await self._deployment_repository.save(deployment)

    async def _find_revision(
        self, workload: Workload, revision_id: int | None
    ) -> WorkloadRevision:
        target_id = revision_id or workload.current_revision_id
        if target_id is None:
            raise RevisionRequiredException

        revision = await self._workload_revision_repository.find_by_id(target_id)
        if not revision or revision.workload_id != workload.pk:
            raise WorkloadRevisionNotFoundException
        return revision

    async def _resolve_spec(self, spec: ContainerSpec) -> ContainerSpec:
        env = list(spec.env)
        for ref in spec.secrets:
            secret = await self._secret_repository.find_by_name(ref.ref)
            if not secret:
                raise SecretNotFoundException
            env.append(
                EnvVar(
                    name=ref.name, value=self._secret_cipher.decrypt(secret.ciphertext)
                )
            )
        return replace(spec, env=env, secrets=[])

    async def _link_container(
        self, deployment: Deployment, command: DeploymentReportCommand
    ) -> int | None:
        if not command.docker_id:
            return None

        workload = await self._workload_repository.find_by_id(deployment.workload_id)
        revision = await self._workload_revision_repository.find_by_id(
            deployment.revision_id
        )
        if not workload or not revision:
            return None

        container = await self._container_repository.upsert_with_revision(
            Container(
                host_id=deployment.host_id,
                workload_id=deployment.workload_id,
                revision_id=deployment.revision_id,
                docker_id=command.docker_id,
                name=self._container_name(workload, revision, deployment),
                image=revision.image,
                state=ContainerState.RUNNING,
            )
        )
        return container.pk

    async def _abort(self, deployment: Deployment, error_message: str) -> None:
        deployment.status = DeploymentStatus.FAILED
        deployment.error_message = error_message
        deployment.finished_at = datetime.now(UTC)
        await self._deployment_repository.save(deployment)
        return None

    def _container_name(
        self, workload: Workload, revision: WorkloadRevision, deployment: Deployment
    ) -> str:
        return f"{workload.name}-r{revision.revision}-d{deployment.pk}"
