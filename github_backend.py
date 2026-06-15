import base64
import json
from io import StringIO

import pandas as pd
import requests


class GithubRepoBackend:
    def __init__(self, owner: str, repo: str, branch: str, token: str, data_path: str = "data"):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.token = token
        self.data_path = data_path.strip("/")
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _path(self, filename: str) -> str:
        return f"{self.data_path}/{filename}" if self.data_path else filename

    def _get_file_meta(self, filename: str):
        url = f"{self.base_url}/{self._path(filename)}?ref={self.branch}"
        response = requests.get(url, headers=self.headers, timeout=30)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def read_csv(self, filename: str) -> pd.DataFrame:
        meta = self._get_file_meta(filename)
        if not meta:
            raise FileNotFoundError(f"{filename} not found in GitHub repository.")

        content = base64.b64decode(meta["content"])
        return pd.read_csv(StringIO(content.decode("utf-8")))

    def read_json(self, filename: str):
        meta = self._get_file_meta(filename)
        if not meta:
            raise FileNotFoundError(f"{filename} not found in GitHub repository.")

        content = base64.b64decode(meta["content"])
        return json.loads(content.decode("utf-8"))

    def _write_content(self, content_bytes: bytes, filename: str, message: str):
        existing = self._get_file_meta(filename)

        payload = {
            "message": message,
            "content": base64.b64encode(content_bytes).decode("utf-8"),
            "branch": self.branch,
        }

        if existing and "sha" in existing:
            payload["sha"] = existing["sha"]

        url = f"{self.base_url}/{self._path(filename)}"
        response = requests.put(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()

    def write_csv(self, df: pd.DataFrame, filename: str, message: str):
        content = df.to_csv(index=False).encode("utf-8")
        self._write_content(content, filename, message)

    def write_json(self, data: dict, filename: str, message: str):
        content = json.dumps(data, indent=2).encode("utf-8")
        self._write_content(content, filename, message)
``
