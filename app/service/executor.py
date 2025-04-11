import subprocess
import tempfile
import os
from typing import Tuple


class ExecutorService:

    def __init__(
        self
    ) -> None:
        pass


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
