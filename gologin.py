import httpx
import time


class GoLogin:
    def __init__(self, token):
        self.client = httpx.Client(
            http2=True
        )
        self.client.headers.update({
            "Authorization": f"Bearer {token}",
        })
        self.profile_id = None

    def __get_fingerprints(self, platform: str):
        r = self.client.get(
            "https://api.gologin.com/browser/fingerprint/",
            params={
                "os": platform
        })
        if r.status_code != 200:
            raise Exception()
        return r.json()

    def create_profile(self, name: str, platform: str = "win", browser_type: str = "chrome", proxy: str = None):
        body = {
            "name": name,
            "os": platform,
            "browserType": browser_type,
            "proxy": {
                "mode": "none",
            },
            "audioContext": {
                "mode": "noise"
            },
            "canvas": {
                "mode": "noise"
            },
            "googleServicesEnabled": True
        }
        if proxy:
            body.update({
                "proxy": {
                    "mode": "http",
                    "host": proxy.split("@")[1].split(":")[0],
                    "port": int(proxy.split("@")[1].split(":")[1]),
                    "username": proxy.split("@")[0].split(":")[0],
                    "password": proxy.split("@")[0].split(":")[1],
                }
            })
        fingerprints = self.__get_fingerprints(platform)
        body.update({
            "navigator": fingerprints["navigator"],
            "fonts": {
                "families": fingerprints["fonts"]
            },
            "mediaDevices": fingerprints["mediaDevices"],
            "webGLMetadata": {
                "vendor": fingerprints["webGLMetadata"]["vendor"],
                "renderer": fingerprints["webGLMetadata"]["renderer"],
            },
            "webglParams": fingerprints["webglParams"],
            "devicePixelRatio": fingerprints["devicePixelRatio"],
        })
        r = self.client.post("https://api.gologin.com/browser", json=body)
        if r.status_code != 201:
            raise Exception()
        self.profile_id = r.json()["id"]
        return self.profile_id
    
    def delete_profile(self, profile_id: str = None):
        if not profile_id:
            profile_id = self.profile_id
        r = self.client.delete(f"https://api.gologin.com/browser/{profile_id}")
        if r.status_code != 204:
            raise Exception()

    def start_profile(self, profile_id: str = None):
        if not profile_id:
            profile_id = self.profile_id
        r = self.client.post("http://localhost:36912/browser/start-profile", json={"profileId": profile_id, "sync": True})
        if r.status_code != 200:
            raise Exception()
        return r.json()["wsUrl"]

    def stop_profile(self, profile_id: str = None):
        if not profile_id:
            profile_id = self.profile_id
        r = self.client.post("http://localhost:36912/browser/stop-profile", json={"profileId": profile_id})
        if r.status_code != 204:
            raise Exception()