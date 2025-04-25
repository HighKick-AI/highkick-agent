import uuid
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
        self._config_yaml = self._load_config(self._agent_config.CONFIG_PATH)
        print(self._config_yaml)

        self._python_env = self._config_yaml["python"]["env"]
        print(self._python_env)

        self._output_dir = self._config_yaml["output"]["directory"]
        print(self._output_dir)

        self._spark_host = self._config_yaml["spark"]["host"]
        print(self._spark_host)

        self._spark_port = self._config_yaml["spark"]["port"]
        print(self._spark_port)


    def _load_config(self, path: str):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config


    def configure_script(self, script: str) -> str:
        databases = self._config_yaml["databases"]
        result = script
        for db in databases:
            variables = db["vars"]
            print(variables)
            for kv in variables:
                key = next(iter(kv))
                val = kv[key]
                result = result.replace("{{" + key + "}}", str(val))

        ## Name of the spark output directory
        filename = os.path.join(self._output_dir, f"{str(uuid.uuid4())}.json")
        result = result.replace("{{output_file}}", filename)
        result = result.replace("{{spark_host}}", self._spark_host)
        result = result.replace("{{spark_port}}", str(self._spark_port))

        return {
            "script": result,
            "output_dir": filename
        }


    def execute_script(self, script: str) -> Tuple[str, str]:
        python_bin = os.path.join(self._python_env, "bin", "python")

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
