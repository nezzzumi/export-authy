import glob
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import List

import requests
from websockets.sync.client import connect

from .exceptions import AuthyInstallationNotFound, AuthyNotFound, SecretsNotFound


@dataclass
class Secret:
    name: str
    secret: str
    period: int


@dataclass
class InstalledVersion:
    version: str
    path: str


class Authy:
    OUTPUT_DIR: str = "installers"
    EXECUTABLE: str = "Authy Desktop.exe"

    def __init__(self) -> None:
        local_path = os.getenv("LOCALAPPDATA")

        if not local_path:
            raise EnvironmentError("LOCALAPPDATA not found.")

        self.authy_local_path = os.path.join(local_path, "authy")
        self.installed_versions = self._get_installed_versions()

    def _get_installed_versions(self) -> List[InstalledVersion]:
        """List versions installed in the %LOCALAPPDATA%/authy folder

        Returns:
            List[InstalledVersion]: a list of versions
        """

        dirs = glob.glob("app-*", root_dir=self.authy_local_path)

        return [
            InstalledVersion(
                version=d.removeprefix("app-"),
                path=os.path.join(self.authy_local_path, d),
            )
            for d in dirs
        ]

    def _rename_updater(self, disable: bool):
        """After the installation, the Authy will perform an auto-udpdate.
        This method disables the updater

        Args:
            disable (bool): disable or enable the updater
        """

        src_exe = "Update.exe" if disable else "Update.exe.old"
        dst_exe = "Update.exe.old" if disable else "Update.exe"

        src = os.path.join(self.authy_local_path, src_exe)
        dst = os.path.join(self.authy_local_path, dst_exe)

        if not os.path.exists(src):
            return

        os.rename(src, dst)

    def _get_version(self, version: str) -> InstalledVersion | None:
        for installed_version in self.installed_versions:
            if installed_version.version == version:
                return installed_version

    def _already_installed(self, version: str = "2.2.3") -> bool:
        """Check if a specific version is installed

        Args:
            version (str): the version

        Returns:
            bool: True if is installed, otherwise False
        """

        return self._get_version(version) is not None

    def install_authy(self, force: bool = False):
        """Install Authy

        Args:
            force (bool, optional): force download and installation. Defaults to False.
        """

        if self._already_installed() and not force:
            print("[i] authy detected, skipping installation...")
            return

        installer_path = os.path.join(self.OUTPUT_DIR, "authy_2.2.3.exe")

        if os.path.exists(installer_path):
            print("[i] installer detected. use -f to overwrite it.")
        else:
            print("[i] downloading authy 2.2.3...")
            installer_path = self._download_authy()

        print("[i] installing authy")
        os.system(installer_path)
        self._rename_updater(disable=True)

        print(
            "[+] please log in your account and unlock your secrets. after that, run the script again with the -e or -d option"
        )

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
                file.write(response.content)  # type: ignore

        return output

    def _get_authy_websocket(self) -> str:
        """Get the websocket of CDP

        Raises:
            AuthyNotFound: if authy is not found

        Returns:
            str: the websocket url
        """

        response = requests.get("http://127.0.0.1:1337/json")
        response_json = response.json()

        for target in response_json:
            if target["url"].endswith("/app.asar/main.html"):
                return target["webSocketDebuggerUrl"]

        raise AuthyNotFound("target not found. is the Authy open?")

    def _wait_for_authy(self, ws_url: str):
        """Wait for authy to load the secrets (max 10 seconds)

        Args:
            ws_url (str): the websocket url

        Raises:
            SecretsNotFound: if zero secrets are returned from Authy
        """

        tries = 1

        with connect(ws_url) as ws:
            print("[i] waiting for authy...")
            while tries < 10:
                payload = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "appManager.getModel()"},
                }

                ws.send(json.dumps(payload))
                result = json.loads(ws.recv())
                result_description = result["result"]["result"]["description"]

                if re.search(r"Array\([1-9]*\)", result_description):
                    print("[*] secrets loaded\n")
                    return

                tries += 1

                time.sleep(1)

        raise SecretsNotFound("secrets didn't load or you have no secrets")

    def _dump_secrets(self) -> List[Secret]:
        """Dump secrets from Authy

        Raises:
            AuthyInstallationNotFound: if Authy is not installed

        Returns:
            List[Secret]: list of secrets
        """

        if not (version := self._get_version("2.2.3")):
            raise AuthyInstallationNotFound(
                "Authy 2.2.3 is not installed. try the --install option."
            )

        subprocess.run(
            ["taskkill.exe", "/f", "/im", "Authy Desktop.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        process = subprocess.Popen(
            [
                os.path.join(version.path, self.EXECUTABLE),
                "--remote-debugging-port=1337",
                "--headless",
            ],
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        ws_url = self._get_authy_websocket()
        self._wait_for_authy(ws_url)

        with connect(ws_url) as ws:
            payload = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "function hex_to_b32(e){let t='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',r=[];for(let n=0;n<e.length;n+=2)r.push(parseInt(e.substr(n,2),16));let d=0,o=0,s='';for(let u=0;u<r.length;u++)for(o=o<<8|r[u],d+=8;d>=5;)s+=t[o>>>d-5&31],d-=5;return d>0&&(s+=t[o<<5-d&31]),s}function dump_secrets(){let e=[];return appManager.getModel().map(function(t){var r=t.secretSeed;void 0===r&&(r=t.encryptedSeed);var n=!1===t.markedForDeletion?t.decryptedSeed:hex_to_b32(r),d=7===t.digits?10:30;e.push({name:t.name,secret:n,period:d})}),JSON.stringify(e)}dump_secrets();"  # noqa
                },
            }

            ws.send(json.dumps(payload))
            result = json.loads(ws.recv())

            secrets_json = json.loads(result["result"]["result"]["value"])
            secrets = []

            for secret in secrets_json:
                secrets.append(
                    Secret(
                        name=secret.get("name"),
                        secret=secret.get("secret"),
                        period=secret.get("period"),
                    )
                )

        process.kill()

        return secrets

    def print_secrets(self):
        secrets = self._dump_secrets()

        for secret in secrets:
            print(f"Name: {secret.name}")
            print(f"Secret: {secret.secret}")
            print(f"Period: {secret.period}")
            print()

    def export(self):
        secrets_dict = [secret.__dict__ for secret in self._dump_secrets()]

        print(json.dumps(secrets_dict))

    def recover_updater(self):
        self._rename_updater(disable=False)
