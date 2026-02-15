import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"
API_BASE_URL = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(self.app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        if not self.app.config.bot:
            self.logger.error("Bot configuration not found")
            return

        params = {
            "group_id": self.app.config.bot.group_id,
            "access_token": self.app.config.bot.token
        }

        url = self._build_query(API_BASE_URL, "groups.getLongPollServer", params)
        async with self.session.get(url) as resp:
            data = await resp.json()
            response = data.get("response", {})
            self.key = response.get("key")
            self.server = response.get("server")
            self.ts = response.get("ts")

    async def poll(self):
        if not self.server or not self.key or self.ts is None:
            await self._get_long_poll_service()
            if not self.server or not self.key or self.ts is None:
                return []

        params = {
            "key": self.key,
            "ts": self.ts,
            "wait": 25,
            "act": "a_check"
        }

        async with self.session.get(
                f"{self.server}?{urlencode(params)}"
        ) as resp:
            data = await resp.json()

            if "ts" in data:
                self.ts = data["ts"]

            updates = []
            if "updates" in data:
                for update_data in data["updates"]:
                    if update_data.get("type") == "message_new":
                        message_data = update_data.get("object", {}).get("message", {})
                        update = Update(
                            type="message_new",
                            object=UpdateObject(
                                message=UpdateMessage(
                                    from_id=message_data.get("from_id"),
                                    text=message_data.get("text", ""),
                                    id=message_data.get("id")
                                )
                            )
                        )
                        updates.append(update)
            return updates

    async def send_message(self, message: Message) -> None:
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "random_id": 0,
            "access_token": self.app.config.bot.token
        }

        url = self._build_query(API_BASE_URL, "messages.send", params)
        async with self.session.get(url) as resp:
            await resp.json()