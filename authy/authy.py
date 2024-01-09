from typing import List
import requests
import os
from dataclasses import dataclass
import glob


@dataclass
class InstalledVersion:
    version: str
    path: str


class Authy:
    OUTPUT_DIR: str = "installers"

    def __init__(self) -> None:
        self.installed_versions = self._get_installed_versions()

    def _get_installed_versions(self) -> List[InstalledVersion]:
        local_path = os.getenv("LOCALAPPDATA")

        if not local_path:
            raise Exception("LOCALAPPDATA not found.")

        local_authy_path = os.path.join(local_path, "authy")

        dirs = glob.glob("app-*", root_dir=local_authy_path)

        return [
            InstalledVersion(
                version=d.removeprefix("app-"), path=os.path.join(local_path, d)
            )
            for d in dirs
        ]

    def _already_installed(self, version: str = "2.2.3") -> bool:
        return any(
            [True if v.version == version else False for v in self.installed_versions]
        )

    def install_authy(self, force: bool = False):
        if self._already_installed() and not force:
            print("[i] authy detected, skiping installation...")
            return

        installer_path = self._download_authy()
        os.system(installer_path)

    def _download_authy(self, force: bool = False) -> str:
        """Download a specific version of Authy (2.2.3)

        Returns:
            str: path of the downloaded file
        """

        if not os.path.exists(self.OUTPUT_DIR):
            os.mkdir(self.OUTPUT_DIR)

        response = requests.get(
            "https://pkg.authy.com/authy/stable/2.2.3/win32/x64/Authy%20Desktop%20Setup%202.2.3.exe"
        )

        output = os.path.join(self.OUTPUT_DIR, "authy_2.2.3.exe")

        if not os.path.exists(output) or force:
            with open(output, "wb") as file:
                file.write(response.content)

        return output

    def _delete_new_version(self):
        ...
