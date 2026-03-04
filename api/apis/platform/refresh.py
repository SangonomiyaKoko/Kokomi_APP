from api.loggers import ExceptionLogger
from api.models import PlatformModel
from api.middlewares import AccessManager, TokenManager
from api.response import JSONResponse


class RefreshAPI:
    @staticmethod
    @ExceptionLogger.handle_program_exception_async
    async def refreshVehicles(server: str):
        result = await ExternalAPI.get_vehicles_data(server)
        return result
    
    @staticmethod
    @ExceptionLogger.handle_program_exception_async
    async def refreshConfig():
        data = {
            'blacklist': {},
            'userlist': {}
        }
        db_config = await PlatformModel.load_config()
        ip_count, user_count, clan_count = AccessManager().reload(
            data=db_config.get('blacklist', {})
        )
        data['blacklist'] = {
            'ip': ip_count,
            'user': user_count,
            'clan': clan_count
        }
        root_users, regular_users = TokenManager().reload(
            data=db_config.get('token', {})
        )
        data['userlist'] = {
            'root': root_users,
            'user': regular_users
        }
        return JSONResponse.get_success_response(data)