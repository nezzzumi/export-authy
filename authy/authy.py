import glob
import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import List

import requests
from websockets.sync.client import connect


@dataclass
class InstalledVersion:
    version: str
    path: str


class Authy:
    OUTPUT_DIR: str = "installers"
    EXECUTABLE: str = "Authy Desktop.exe"

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
                version=d.removeprefix("app-"), path=os.path.join(local_authy_path, d)
            )
            for d in dirs
        ]

    def get_version(self, version: str) -> InstalledVersion | None:
        for installed_version in self.installed_versions:
            if installed_version.version == version:
                return installed_version

    def _already_installed(self, version: str = "2.2.3") -> bool:
        if self.get_version(version):
            return True

        return False

    def install_authy(self, force: bool = False):
        if self._already_installed() and not force:
            print("[i] authy detected, skipping installation...")
            return

        print("[i] downloading authy 2.2.3...")
        installer_path = self._download_authy()
        print("[i] opening authy")
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

    def _get_authy_websocket(self) -> str:
        response = requests.get("http://127.0.0.1:1337/json")
        response_json = response.json()

        for target in response_json:
            if target["url"].endswith("/app.asar/main.html"):
                return target["webSocketDebuggerUrl"]

        raise Exception("Target not found. Is the Authy open?")

    def _wait_for_authy(self, ws_url: str):
        tries = 1

        with connect(ws_url) as ws:
            while tries < 10:
                payload = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "appManager.getModel()"},
                }

                ws.send(json.dumps(payload))
                result = json.loads(ws.recv())

                if result["result"]["result"]["description"] != "Array(0)":
                    return

                tries += 1

                time.sleep(1)

        raise Exception("secrets didn't load or you have no secrets")

    def export(self):
        if not (version := self.get_version("2.2.3")):
            raise Exception("Authy 2.2.3 is not installed. Try the --install option.")

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
                    "expression": "function hex_to_b32(e){let t='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',r=[];for(let n=0;n<e.length;n+=2)r.push(parseInt(e.substr(n,2),16));let d=0,o=0,s='';for(let u=0;u<r.length;u++)for(o=o<<8|r[u],d+=8;d>=5;)s+=t[o>>>d-5&31],d-=5;return d>0&&(s+=t[o<<5-d&31]),s}function dump_secrets(){let e=[];return appManager.getModel().map(function(t){var r=t.secretSeed;void 0===r&&(r=t.encryptedSeed);var n=!1===t.markedForDeletion?t.decryptedSeed:hex_to_b32(r);t.digits,e.push({name:t.name,secret:n})}),JSON.stringify(e)}dump_secrets();"  # noqa
                },
            }

            ws.send(json.dumps(payload))
            result = json.loads(ws.recv())

            secrets = json.loads(result["result"]["result"]["value"])
            # TODO: improve the output
            print(secrets)

        process.kill()
