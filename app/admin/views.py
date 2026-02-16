from app.web.app import View
from app.admin.schemes import AdminSchema
from app.web.utils import json_response
from app.web.mixins import AuthRequiredMixin

from aiohttp import web
from aiohttp_session import new_session
from aiohttp_apispec import request_schema, response_schema


class AdminLoginView(View):

    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = await self.request.json()
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise web.HTTPBadRequest

        admin_from_db = await self.store.admins.get_by_email(email)
        if not admin_from_db or not admin_from_db.password != password:
            raise web.HTTPForbidden

        session = await new_session(request=self.request)
        admin = AdminSchema().dump(admin_from_db)
        session["admin"] = admin
        return json_response(data=admin)


class AdminCurrentView(AuthRequiredMixin, View):

    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
