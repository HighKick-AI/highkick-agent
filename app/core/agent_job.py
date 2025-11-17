import json
from pathlib import Path
from typing import Optional
from schemas.agent import StatusSchema


class AgentJob:

    def __init__(self, base_dir: str, id: str):
        self._base_dir = base_dir
        self._id = id

    @property
    def job_dir(self) -> Path:
        return Path(self._base_dir) / self._id

    def get_id(self) -> str:
        return self._id

    # -------------------------
    # Status
    # -------------------------

    def get_status(self) -> Optional[StatusSchema]:
        path = self.job_dir / "status.json"
        if not path.exists():
            return None

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Pydantic v2
        return StatusSchema.model_validate(data)

    def set_status(self, status: StatusSchema) -> None:
        path = self.job_dir / "status.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(status.model_dump(), f, indent=2)

    # -------------------------
    # std_io
    # -------------------------

    def get_std_output(self) -> Optional[str]:
        path = self.job_dir / "std_output.txt"
        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")
    
    def get_std_output_path(self) -> Optional[Path]:
        path = self.job_dir / "std_output.txt"
        if not path.exists():
            return None

        return path

    def set_std_output(self, content: str) -> None:
        path = self.job_dir / "std_output.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # -------------------------
    # error
    # -------------------------

    def get_error(self) -> Optional[str]:
        path = self.job_dir / "error.txt"
        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")
    
    def get_error_path(self) -> Optional[Path]:
        path = self.job_dir / "error.txt"
        if not path.exists():
            return None

        return path

    def set_error(self, content: str) -> None:
        path = self.job_dir / "error.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # -------------------------
    # data
    # -------------------------

    def get_data(self) -> Optional[str]:
        path = self.job_dir / "data.json"
        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")
    
    def get_data_path_str(self) -> str:
        path = self.job_dir / "data.json"
        return str(path)

    def get_data_path(self) -> Optional[Path]:
        path = self.job_dir / "data.json"
        if not path.exists():
            return None
        return path

    def set_data(self, content: str) -> None:
        path = self.job_dir / "data.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
