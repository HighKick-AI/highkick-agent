import yaml
import subprocess
import tempfile
import os
from typing import Tuple

from app.core.settings import AgentConfig


class ExecutorService:

    def __init__(
        self,
        agent_config: AgentConfig
    ) -> None:
        self._agent_config = agent_config
        print("Executor initialized")


    def execute_script(script: str, env_path: str) -> Tuple[str, str]:
        python_bin = os.path.join(env_path, "bin", "python")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(script)
            tmp_file_path = tmp_file.name

        try:
            result = subprocess.run(
                [python_bin, tmp_file_path],
                capture_output=True,
                text=True
            )
            return result.stdout, result.stderr
        finally:
            os.remove(tmp_file_path)
