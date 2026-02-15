from aiohttp.web_exceptions import HTTPUnauthorized
class AuthRequiredMixin:
    # TODO: можно использовать эту mixin-заготовку для реализации проверки авторизации во View
    async def _iter(self):
        if not self.request.admin:
            raise HTTPUnauthorized(reason="Authentication required")
        return await super()._iter()