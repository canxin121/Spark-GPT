from typing import TYPE_CHECKING, Any

from nonebot.drivers import Request
from nonebot.utils import escape_tag

from ..utils import log, json_loads, decompress_data
from ..exception import (
    ActionFailed,
    NetworkError,
    ApiNotAvailable,
    RateLimitException,
    UnauthorizedException,
    DiscordAdapterException,
)

if TYPE_CHECKING:
    from ..bot import Bot
    from ..adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    try:
        request.timeout = adapter.discord_config.discord_api_timeout
        request.proxy = adapter.discord_config.discord_proxy
        data = await adapter.request(request)
        log(
            "TRACE",
            f"API code: {data.status_code} response: {escape_tag(str(data.content))}",
        )
        if data.status_code in (200, 201, 204):
            return data.content and json_loads(
                decompress_data(data.content, adapter.discord_config.discord_compress)
            )
        elif data.status_code in (401, 403):
            raise UnauthorizedException(data)
        elif data.status_code in (404, 405):
            raise ApiNotAvailable
        elif data.status_code == 429:
            raise RateLimitException(data)
        else:
            raise ActionFailed(data)
    except DiscordAdapterException:
        raise
    except Exception as e:
        raise NetworkError("API request failed") from e
