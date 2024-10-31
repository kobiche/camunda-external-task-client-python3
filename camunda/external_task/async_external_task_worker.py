import asyncio
from typing import Any, Callable, Dict, List, Optional

from camunda.client.async_external_task_client import AsyncExternalTaskClient
from camunda.client.external_task_client import ENGINE_LOCAL_BASE_URL
from camunda.external_task.async_external_task_executor import AsyncExternalTaskExecutor
from camunda.external_task.external_task import ExternalTask
from camunda.utils.auth_basic import obfuscate_password
from camunda.utils.log_utils import log_with_context
from camunda.utils.utils import get_exception_detail


class AsyncExternalTaskWorker:
    DEFAULT_SLEEP_SECONDS = 300

    def __init__(
        self,
        worker_id: str,
        base_url: str = ENGINE_LOCAL_BASE_URL,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.config = config or {}
        self.worker_id = worker_id
        self.client = AsyncExternalTaskClient(self.worker_id, base_url, self.config)
        self.executor = AsyncExternalTaskExecutor(self.worker_id, self.client)
        self._log_with_context(
            f"Created new External Task Worker with config: {obfuscate_password(self.config)}"
        )

    async def subscribe(
        self,
        topic_handlers: Dict[str, Callable[[ExternalTask], Any]],
        process_variables: Optional[Dict[str, Any]] = None,
        variables: Optional[List[str]] = None,
    ):
        tasks = [
            self._fetch_and_execute_safe(topic, action, process_variables, variables)
            for topic, action in topic_handlers.items()
        ]
        await asyncio.gather(*tasks)

    async def _fetch_and_execute_safe(
        self,
        topic_name: str,
        action: Callable[[ExternalTask], Any],
        process_variables: Optional[Dict[str, Any]] = None,
        variables: Optional[List[str]] = None,
    ):
        sleep_seconds = self._get_sleep_seconds()
        while True:
            try:
                await self.fetch_and_execute(topic_name, action, process_variables, variables)
            except Exception as e:
                self._log_with_context(
                    f"Error fetching and executing tasks: {get_exception_detail(e)} "
                    f"for topic={topic_name} with Process variables: {process_variables}. "
                    f"Retrying after {sleep_seconds} seconds",
                    exc_info=True,
                )
            await asyncio.sleep(sleep_seconds)

    async def fetch_and_execute(
        self,
        topic_name: str,
        action: Callable[[ExternalTask], Any],
        process_variables: Optional[Dict[str, Any]] = None,
        variables: Optional[List[str]] = None,
    ):
        self._log_with_context(
            f"Fetching and executing external tasks for Topic: {topic_name} "
            f"with Process variables: {process_variables}"
        )
        resp_json = await self._fetch_and_lock(topic_name, process_variables, variables)
        tasks = self._parse_response(resp_json, topic_name, process_variables)
        if not tasks:
            self._log_with_context(
                f"No external tasks found for Topic: {topic_name}, Process variables: {process_variables}"
            )
            return
        await self._execute_tasks(tasks, action)

    async def _fetch_and_lock(
        self,
        topic_name: str,
        process_variables: Optional[Dict[str, Any]] = None,
        variables: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        self._log_with_context(
            f"Fetching and locking external tasks for Topic: {topic_name} "
            f"with Process variables: {process_variables}"
        )
        return await self.client.fetch_and_lock([topic_name], process_variables, variables)

    def _parse_response(
        self,
        resp_json: List[Dict[str, Any]],
        topic_name: str,
        process_variables: Optional[Dict[str, Any]],
    ) -> List[ExternalTask]:
        tasks = [ExternalTask(context) for context in resp_json or []]
        tasks_count = len(tasks)
        self._log_with_context(
            f"{tasks_count} external task(s) found for "
            f"Topic: {topic_name}, Process variables: {process_variables}"
        )
        return tasks

    async def _execute_tasks(
        self, tasks: List[ExternalTask], action: Callable[[ExternalTask], Any]
    ):
        await asyncio.gather(
            *(self._execute_task(task, action) for task in tasks), return_exceptions=True
        )

    async def _execute_task(self, task: ExternalTask, action: Callable[[ExternalTask], Any]):
        try:
            await self.executor.execute_task(task, action)
        except Exception as e:
            self._log_with_context(
                f"Error when executing task: {get_exception_detail(e)}",
                topic=task.get_topic_name(),
                task_id=task.get_task_id(),
                log_level="error",
                exc_info=True,
            )
            # Handle the exception as needed (e.g., report failure, continue)

    def _log_with_context(
        self,
        msg: str,
        topic: Optional[str] = None,
        task_id: Optional[str] = None,
        log_level: str = "info",
        **kwargs: Any,
    ):
        context = {"WORKER_ID": str(self.worker_id), "TOPIC": topic, "TASK_ID": task_id}
        log_with_context(msg, context=context, log_level=log_level, **kwargs)

    def _get_sleep_seconds(self) -> int:
        return self.config.get("sleepSeconds", self.DEFAULT_SLEEP_SECONDS)
