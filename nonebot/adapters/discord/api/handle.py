from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, List, Literal, Optional

from pydantic import parse_obj_as
from nonebot.drivers import Request

from .model import *
from .request import _request
from .utils import parse_data, parse_forum_thread_message

if TYPE_CHECKING:
    from ..bot import Bot
    from ..adapter import Adapter


# Application Role Connection Metadata
# see https://discord.com/developers/docs/resources/application-role-connection-metadata


async def _get_application_role_connection_metadata_records(
    adapter: "Adapter", bot: "Bot", application_id: SnowflakeType
) -> List[ApplicationRoleConnectionMetadata]:
    """get application role connection metadata records

    see https://discord.com/developers/docs/resources/application-role-connection-metadata#get-application-role-connection-metadata-records
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url
        / f"applications/{application_id}/role-connections/metadata",
    )
    return parse_obj_as(
        List[ApplicationRoleConnectionMetadata], await _request(adapter, bot, request)
    )


async def _update_application_role_connection_metadata_records(
    adapter: "Adapter", bot: "Bot", application_id: SnowflakeType
) -> List[ApplicationRoleConnectionMetadata]:
    """get application role connection metadata records

    see https://discord.com/developers/docs/resources/application-role-connection-metadata#get-application-role-connection-metadata-records
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url
        / f"applications/{application_id}/role-connections/metadata",
    )
    return parse_obj_as(
        List[ApplicationRoleConnectionMetadata], await _request(adapter, bot, request)
    )


async def _get_guild_audit_log(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> AuditLog:
    """get guild audit log

    see https://discord.com/developers/docs/resources/audit-log#get-guild-audit-log"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/audit-logs",
        params=data,
    )
    return parse_obj_as(AuditLog, await _request(adapter, bot, request))


async def _list_auto_moderation_rules_for_guild(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[AutoModerationRule]:
    """list auto moderation rules for guild

    see https://discord.com/developers/docs/resources/auto-moderation#list-auto-moderation-rules-for-guild
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/auto-moderation/rules",
    )
    return parse_obj_as(List[AutoModerationRule], await _request(adapter, bot, request))


async def _get_auto_moderation_rule(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, rule_id: SnowflakeType
) -> AutoModerationRule:
    """get auto moderation rule

    see https://discord.com/developers/docs/resources/auto-moderation#get-auto-moderation-rule
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/auto-moderation/rules/{rule_id}",
    )
    return parse_obj_as(AutoModerationRule, await _request(adapter, bot, request))


async def _create_auto_moderation_rule(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> AutoModerationRule:
    """create auto moderation rule

    see https://discord.com/developers/docs/resources/auto-moderation#create-auto-moderation-rule
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = CreateAndModifyAutoModerationRuleParams.parse_obj(data).dict(
        exclude_none=True
    )
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/auto-moderation/rules",
        json=data,
    )
    return parse_obj_as(AutoModerationRule, await _request(adapter, bot, request))


async def _modify_auto_moderation_rule(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    rule_id: SnowflakeType,
    **data,
) -> AutoModerationRule:
    """modify auto moderation rule

    see https://discord.com/developers/docs/resources/auto-moderation#modify-auto-moderation-rule
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = CreateAndModifyAutoModerationRuleParams.parse_obj(data).dict(
        exclude_none=True
    )
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/auto-moderation/rules/{rule_id}",
        json=data,
    )
    return parse_obj_as(AutoModerationRule, await _request(adapter, bot, request))


async def _delete_auto_moderation_rule(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    rule_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """delete auto moderation rule

    see https://discord.com/developers/docs/resources/auto-moderation#delete-auto-moderation-rule
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/auto-moderation/rules/{rule_id}",
    )
    await _request(adapter, bot, request)


async def _get_channel(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
) -> Channel:
    """get channel

    see https://discord.com/developers/docs/resources/channel#get-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}",
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _modify_DM(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Channel:
    """modify channel

    see https://discord.com/developers/docs/resources/channel#modify-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"channels/{channel_id}",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _modify_channel(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Channel:
    """modify channel

    see https://discord.com/developers/docs/resources/channel#modify-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = ModifyChannelParams.parse_obj(data).dict(exclude_unset=True)
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"channels/{channel_id}",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _modify_thread(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Channel:
    """modify channel

    see https://discord.com/developers/docs/resources/channel#modify-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"channels/{channel_id}",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _delete_channel(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    reason: Optional[str] = None,
) -> Channel:
    """delete channel

    see https://discord.com/developers/docs/resources/channel#deleteclose-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}",
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _get_channel_messages(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> List[MessageGet]:
    """get channel messages

    see https://discord.com/developers/docs/resources/channel#get-channel-messages"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/messages",
        params=data,
    )
    return parse_obj_as(List[MessageGet], await _request(adapter, bot, request))


async def _get_channel_message(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, message_id: SnowflakeType
) -> MessageGet:
    """get channel message

    see https://discord.com/developers/docs/resources/channel#get-channel-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}",
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _create_message(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> MessageGet:
    """create message

    see https://discord.com/developers/docs/resources/channel#create-message
    """
    params = parse_data(data, MessageSend)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/messages",
        **params,
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _crosspost_message(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, message_id: SnowflakeType
) -> MessageGet:
    """crosspost message

    see https://discord.com/developers/docs/resources/channel#crosspost-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}/crosspost",
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _create_reaction(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    emoji: str,
    emoji_id: Optional[SnowflakeType] = None,
) -> None:
    """create reaction

    see https://discord.com/developers/docs/resources/channel#create-reaction"""
    if emoji_id is not None:
        emoji = f"{emoji}:{emoji_id}"
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url
        / f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/@me",
    )
    await _request(adapter, bot, request)


async def _delete_own_reaction(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    emoji: str,
    emoji_id: Optional[SnowflakeType] = None,
) -> None:
    """delete own reaction

    see https://discord.com/developers/docs/resources/channel#delete-own-reaction"""
    if emoji_id is not None:
        emoji = f"{emoji}:{emoji_id}"
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url
        / f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/@me",
    )
    await _request(adapter, bot, request)


async def _delete_user_reaction(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    user_id: SnowflakeType,
    emoji: str,
    emoji_id: Optional[SnowflakeType] = None,
) -> None:
    """delete user reaction

    see https://discord.com/developers/docs/resources/channel#delete-user-reaction"""
    if emoji_id is not None:
        emoji = f"{emoji}:{emoji_id}"
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url
        / f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/{user_id}",
    )
    await _request(adapter, bot, request)


async def _get_reactions(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    emoji: str,
    emoji_id: Optional[SnowflakeType] = None,
    **params,
) -> List[User]:
    """get reactions

    see https://discord.com/developers/docs/resources/channel#get-reactions"""
    if emoji_id is not None:
        emoji = f"{emoji}:{emoji_id}"
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url
        / f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}",
        params=params,
    )
    return parse_obj_as(List[User], await _request(adapter, bot, request))


async def _delete_all_reactions(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
):
    """

    see https://discord.com/developers/docs/resources/channel#delete-all-reactions
    """
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}/reactions",
    )
    await _request(adapter, bot, request)


async def _delete_all_reactions_for_emoji(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    emoji: str,
    emoji_id: Optional[SnowflakeType] = None,
):
    """

    see https://discord.com/developers/docs/resources/channel#delete-all-reactions
    """
    if emoji_id is not None:
        emoji = f"{emoji}:{emoji_id}"
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url
        / f"channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}",
    )
    await _request(adapter, bot, request)


async def _edit_message(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    **data,
) -> MessageGet:
    """see https://discord.com/developers/docs/resources/channel#edit-message"""
    params = parse_data(data, MessageSend)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}",
        **params,
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _delete_message(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/channel#delete-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}",
    )
    await _request(adapter, bot, request)


async def _bulk_delete_message(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
):
    """https://discord.com/developers/docs/resources/channel#bulk-delete-messages"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/messages/bulk-delete",
        json=data,
    )
    await _request(adapter, bot, request)


async def _edit_channel_permissions(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    overwrite_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/channel#edit-channel-permissions"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"channels/{channel_id}/permissions/{overwrite_id}",
    )
    await _request(adapter, bot, request)


async def _get_channel_invites(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
) -> List[Invite]:
    """https://discord.com/developers/docs/resources/channel#get-channel-invites"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/invites",
    )
    return parse_obj_as(List[Invite], await _request(adapter, bot, request))


async def _create_channel_invite(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Invite:
    """https://discord.com/developers/docs/resources/channel#create-channel-invite"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/invites",
        json=data,
    )
    return parse_obj_as(Invite, await _request(adapter, bot, request))


async def _delete_channel_permission(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    overwrite_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/channel#delete-channel-permission"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/permissions/{overwrite_id}",
    )
    await _request(adapter, bot, request)


async def _follow_announcement_channel(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> FollowedChannel:
    """https://discord.com/developers/docs/resources/channel#follow-news-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/followers",
        json=data,
    )
    return parse_obj_as(FollowedChannel, await _request(adapter, bot, request))


async def _trigger_typing_indicator(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
):
    """https://discord.com/developers/docs/resources/channel#trigger-typing-indicator"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/typing",
    )
    await _request(adapter, bot, request)


async def _get_pinned_messages(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
) -> List[MessageGet]:
    """https://discord.com/developers/docs/resources/channel#get-pinned-messages"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/pins",
    )
    return parse_obj_as(List[MessageGet], await _request(adapter, bot, request))


async def _pin_message(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/channel#add-pinned-channel-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"channels/{channel_id}/pins/{message_id}",
    )
    await _request(adapter, bot, request)


async def _unpin_message(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/channel#delete-pinned-channel-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/pins/{message_id}",
    )
    await _request(adapter, bot, request)


async def _group_DM_add_recipient(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    user_id: SnowflakeType,
    **data,
):
    """https://discord.com/developers/docs/resources/channel#group-dm-add-recipient"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"channels/{channel_id}/recipients/{user_id}",
        json=data,
    )
    await _request(adapter, bot, request)


async def _group_DM_remove_recipient(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, user_id: SnowflakeType
):
    """https://discord.com/developers/docs/resources/channel#group-dm-remove-recipient"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/recipients/{user_id}",
    )
    await _request(adapter, bot, request)


async def _start_thread_from_message(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    message_id: SnowflakeType,
    **data,
) -> Channel:
    """https://discord.com/developers/docs/resources/channel#start-thread-with-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/messages/{message_id}/threads",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _start_thread_without_message(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Channel:
    """https://discord.com/developers/docs/resources/channel#start-thread-without-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/threads",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _start_thread_in_forum_channel(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Channel:
    """https://discord.com/developers/docs/resources/channel#start-thread-in-forum-channel"""
    params = parse_forum_thread_message(data)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/threads",
        **params,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _join_thread(adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType):
    """https://discord.com/developers/docs/resources/channel#join-thread"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"channels/{channel_id}/thread-members/@me",
    )
    await _request(adapter, bot, request)


async def _add_thread_member(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, user_id: SnowflakeType
):
    """https://discord.com/developers/docs/resources/channel#add-thread-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"channels/{channel_id}/thread-members/{user_id}",
    )
    await _request(adapter, bot, request)


async def _leave_thread(adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType):
    """https://discord.com/developers/docs/resources/channel#leave-thread"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/thread-members/@me",
    )
    await _request(adapter, bot, request)


async def _remove_thread_member(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, user_id: SnowflakeType
):
    """https://discord.com/developers/docs/resources/channel#remove-thread-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"channels/{channel_id}/thread-members/{user_id}",
    )
    await _request(adapter, bot, request)


async def _get_thread_member(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    user_id: SnowflakeType,
    **params,
) -> ThreadMember:
    """https://discord.com/developers/docs/resources/channel#get-thread-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/thread-members/{user_id}",
        params=params,
    )
    return parse_obj_as(ThreadMember, await _request(adapter, bot, request))


async def _list_thread_members(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **params
) -> List[ThreadMember]:
    """https://discord.com/developers/docs/resources/channel#list-thread-members"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/thread-members",
        params=params,
    )
    return parse_obj_as(List[ThreadMember], await _request(adapter, bot, request))


async def _list_public_archived_threads(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **params
) -> ArchivedThreadsResponse:
    """https://discord.com/developers/docs/resources/channel#list-public-archived-threads"""
    if before := params.get("before"):
        params["before"] = before.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/threads/archived/public",
        params=params,
    )
    return parse_obj_as(ArchivedThreadsResponse, await _request(adapter, bot, request))


async def _list_private_archived_threads(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **params
) -> ArchivedThreadsResponse:
    """https://discord.com/developers/docs/resources/channel#list-private-archived-threads"""
    if before := params.get("before"):
        params["before"] = before.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/threads/archived/private",
        params=params,
    )
    return parse_obj_as(ArchivedThreadsResponse, await _request(adapter, bot, request))


async def _list_joined_private_archived_threads(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **params
) -> ArchivedThreadsResponse:
    """https://discord.com/developers/docs/resources/channel#list-joined-private-archived-threads"""
    if before := params.get("before"):
        params["before"] = before.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url
        / f"channels/{channel_id}/users/@me/threads/archived/private",
        params=params,
    )
    return parse_obj_as(ArchivedThreadsResponse, await _request(adapter, bot, request))


async def _list_guild_emojis(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Emoji]:
    """https://discord.com/developers/docs/resources/emoji#list-guild-emojis"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/emojis",
    )
    return parse_obj_as(List[Emoji], await _request(adapter, bot, request))


async def _get_guild_emoji(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, emoji_id: SnowflakeType
) -> Emoji:
    """https://discord.com/developers/docs/resources/emoji#get-guild-emoji"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/emojis/{emoji_id}",
    )
    return parse_obj_as(Emoji, await _request(adapter, bot, request))


async def _create_guild_emoji(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Emoji:
    """https://discord.com/developers/docs/resources/emoji#create-guild-emoji"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/emojis",
        json=data,
    )
    return parse_obj_as(Emoji, await _request(adapter, bot, request))


async def _modify_guild_emoji(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    emoji_id: SnowflakeType,
    **data,
) -> Emoji:
    """https://discord.com/developers/docs/resources/emoji#modify-guild-emoji"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/emojis/{emoji_id}",
        json=data,
    )
    return parse_obj_as(Emoji, await _request(adapter, bot, request))


async def _delete_guild_emoji(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    emoji_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/emoji#delete-guild-emoji"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/emojis/{emoji_id}",
    )
    await _request(adapter, bot, request)


async def _create_guild(adapter: "Adapter", bot: "Bot", **data) -> Guild:
    """https://discord.com/developers/docs/resources/guild#create-guild"""
    data = CreateGuildParams.parse_obj(data).dict(exclude_unset=True)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers, method="POST", url=adapter.base_url / "guilds", json=data
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _get_guild(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
) -> Guild:
    """https://discord.com/developers/docs/resources/guild#get-guild"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}",
        params=params,
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _get_guild_preview(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> GuildPreview:
    """https://discord.com/developers/docs/resources/guild#get-guild-preview"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/preview",
    )
    return parse_obj_as(GuildPreview, await _request(adapter, bot, request))


async def _modify_guild(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Guild:
    """https://discord.com/developers/docs/resources/guild#modify-guild"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = ModifyGuildParams.parse_obj(data).dict(exclude_unset=True)
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/preview",
        json=data,
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _delete_guild(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> None:
    """https://discord.com/developers/docs/resources/guild#delete-guild"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_channels(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Channel]:
    """https://discord.com/developers/docs/resources/guild#get-guild-channels"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/channels",
    )
    return parse_obj_as(List[Channel], await _request(adapter, bot, request))


async def _create_guild_channel(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Channel:
    """https://discord.com/developers/docs/resources/guild#create-guild-channel"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = CreateGuildChannelParams.parse_obj(data).dict(exclude_unset=True)
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/channels",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _modify_guild_channel_positions(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Guild:
    """https://discord.com/developers/docs/resources/guild#modify-guild-channel-positions"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/channels",
        json=data,
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _list_active_guild_threads(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> ListActiveGuildThreadsResponse:
    """https://discord.com/developers/docs/resources/guild#list-active-guild-threads"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/threads/active",
    )
    return parse_obj_as(
        ListActiveGuildThreadsResponse, await _request(adapter, bot, request)
    )


async def _get_guild_member(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, user_id: SnowflakeType
) -> GuildMember:
    """https://discord.com/developers/docs/resources/guild#get-guild-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}",
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _list_guild_members(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
) -> List[GuildMember]:
    """https://discord.com/developers/docs/resources/guild#list-guild-members"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/members",
        params=params,
    )
    return parse_obj_as(List[GuildMember], await _request(adapter, bot, request))


async def _search_guild_members(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
) -> List[GuildMember]:
    """https://discord.com/developers/docs/resources/guild#search-guild-members"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/members/search",
        params=params,
    )
    return parse_obj_as(List[GuildMember], await _request(adapter, bot, request))


async def _add_guild_member(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    **data,
) -> GuildMember:
    """https://discord.com/developers/docs/resources/guild#add-guild-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}",
        json=data,
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _modify_guild_member(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    **data,
) -> GuildMember:
    """https://discord.com/developers/docs/resources/guild#modify-guild-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}",
        json=data,
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _modify_current_member(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> GuildMember:
    """https://discord.com/developers/docs/resources/guild#modify-current-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/members/@me",
        json=data,
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _modify_current_user_nick(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> GuildMember:
    """https://discord.com/developers/docs/resources/guild#modify-current-user-nick"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/members/@me/nick",
        json=data,
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _add_guild_member_role(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    role_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/guild#add-guild-member-role"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
    )
    await _request(adapter, bot, request)


async def _remove_guild_member_role(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    role_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/guild#remove-guild-member-role"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}/roles/{role_id}",
    )
    await _request(adapter, bot, request)


async def _remove_guild_member(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    reason: Optional[str] = None,
):
    """https://discord.com/developers/docs/resources/guild#remove-guild-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/members/{user_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_bans(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
) -> List[Ban]:
    """https://discord.com/developers/docs/resources/guild#get-guild-bans"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/bans",
        params=params,
    )
    return parse_obj_as(List[Ban], await _request(adapter, bot, request))


async def _get_guild_ban(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, user_id: SnowflakeType
) -> Ban:
    """https://discord.com/developers/docs/resources/guild#get-guild-ban"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/bans/{user_id}",
    )
    return parse_obj_as(Ban, await _request(adapter, bot, request))


async def _create_guild_ban(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    **data,
) -> None:
    """https://discord.com/developers/docs/resources/guild#create-guild-ban"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"guilds/{guild_id}/bans/{user_id}",
        json=data,
    )
    await _request(adapter, bot, request)


async def _remove_guild_ban(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/guild#remove-guild-ban"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/bans/{user_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_roles(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Role]:
    """https://discord.com/developers/docs/resources/guild#get-guild-roles"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/roles",
    )
    return parse_obj_as(List[Role], await _request(adapter, bot, request))


async def _create_guild_role(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Role:
    """https://discord.com/developers/docs/resources/guild#create-guild-role"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/roles",
        json=data,
    )
    return parse_obj_as(Role, await _request(adapter, bot, request))


async def _modify_guild_role_positions(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> List[Role]:
    """https://discord.com/developers/docs/resources/guild#modify-guild-role-positions"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/roles",
        json=data,
    )
    return parse_obj_as(List[Role], await _request(adapter, bot, request))


async def _modify_guild_role(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    role_id: SnowflakeType,
    **data,
) -> Role:
    """https://discord.com/developers/docs/resources/guild#modify-guild-role"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/roles/{role_id}",
        json=data,
    )
    return parse_obj_as(Role, await _request(adapter, bot, request))


async def _modify_guild_MFA_level(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> None:
    """https://discord.com/developers/docs/resources/guild#modify-guild-mfa-level"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/mfa",
        json=data,
    )
    await _request(adapter, bot, request)


async def _delete_guild_role(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    role_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/guild#delete-guild-role"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/roles/{role_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_prune_count(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Dict[Literal["pruned"], int]:
    """https://discord.com/developers/docs/resources/guild#get-guild-prune-count"""
    if "include_roles" in data:
        data["include_roles"] = ",".join(str(role) for role in data["include_roles"])
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/prune",
        params=data,
    )
    return await _request(adapter, bot, request)


async def _begin_guild_prune(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> Dict[Literal["pruned"], int]:
    """https://discord.com/developers/docs/resources/guild#begin-guild-prune"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/prune",
        json=data,
    )
    return await _request(adapter, bot, request)


async def _get_guild_voice_regions(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[VoiceRegion]:
    """https://discord.com/developers/docs/resources/guild#get-guild-voice-regions"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/regions",
    )
    return parse_obj_as(List[VoiceRegion], await _request(adapter, bot, request))


async def _get_guild_invites(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Invite]:
    """https://discord.com/developers/docs/resources/guild#get-guild-invites"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/invites",
    )
    return parse_obj_as(List[Invite], await _request(adapter, bot, request))


async def _get_guild_integrations(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Integration]:
    """https://discord.com/developers/docs/resources/guild#get-guild-integrations"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/integrations",
    )
    return parse_obj_as(List[Integration], await _request(adapter, bot, request))


async def _delete_guild_integration(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    integration_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/guild#delete-guild-integration"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/integrations/{integration_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_widget_settings(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> GuildWidgetSettings:
    """https://discord.com/developers/docs/resources/guild#get-guild-widget-settings"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/widget",
    )
    return parse_obj_as(GuildWidgetSettings, await _request(adapter, bot, request))


async def _modify_guild_widget(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> GuildWidget:
    """https://discord.com/developers/docs/resources/guild#modify-guild-widget"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/widget",
        json=data,
    )
    return parse_obj_as(GuildWidget, await _request(adapter, bot, request))


async def _get_guild_widget(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> GuildWidget:
    """https://discord.com/developers/docs/resources/guild#get-guild-widget"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/widget.json",
    )
    return parse_obj_as(GuildWidget, await _request(adapter, bot, request))


async def _get_guild_vanity_url(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> Invite:
    """https://discord.com/developers/docs/resources/guild#get-guild-vanity-url"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/vanity-url",
    )
    return parse_obj_as(Invite, await _request(adapter, bot, request))


async def _get_guild_widget_image(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
):
    """https://discord.com/developers/docs/resources/guild#get-guild-widget-image"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/widget.png",
        params=params,
    )
    return await _request(adapter, bot, request)


async def _get_guild_welcome_screen(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> WelcomeScreen:
    """https://discord.com/developers/docs/resources/guild#get-guild-welcome-screen"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/welcome-screen",
    )
    return parse_obj_as(WelcomeScreen, await _request(adapter, bot, request))


async def _modify_guild_welcome_screen(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> WelcomeScreen:
    """https://discord.com/developers/docs/resources/guild#modify-guild-welcome-screen"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = ModifyGuildWelcomeScreenParams.parse_obj(data).dict(exclude_unset=True)
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/welcome-screen",
        json=data,
    )
    return parse_obj_as(WelcomeScreen, await _request(adapter, bot, request))


async def _get_guild_onboarding(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> GuildOnboarding:
    """https://discord.com/developers/docs/resources/guild#get-guild-onboarding"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/onboarding",
    )
    return parse_obj_as(GuildOnboarding, await _request(adapter, bot, request))


async def _modify_current_user_voice_state(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> None:
    """https://discord.com/developers/docs/resources/guild#modify-current-user-voice-state"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/voice-states/@me",
        json=data,
    )
    await _request(adapter, bot, request)


async def _modify_user_voice_state(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    user_id: SnowflakeType,
    **data,
) -> None:
    """https://discord.com/developers/docs/resources/guild#modify-user-voice-state"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/voice-states/{user_id}",
        json=data,
    )
    await _request(adapter, bot, request)


async def _list_scheduled_events_for_guild(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **params
) -> List[GuildScheduledEvent]:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#list-scheduled-events-for-guild"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events",
        params=params,
    )
    return parse_obj_as(
        List[GuildScheduledEvent], await _request(adapter, bot, request)
    )


async def _create_guild_schedule_event(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> GuildScheduledEvent:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#create-guild-scheduled-event"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = CreateGuildScheduledEventParams.parse_obj(data).dict(exclude_none=True)
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events",
        json=data,
    )
    return parse_obj_as(GuildScheduledEvent, await _request(adapter, bot, request))


async def _get_guild_scheduled_event(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    event_id: SnowflakeType,
    **params,
) -> GuildScheduledEvent:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#get-guild-scheduled-event"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events/{event_id}",
        params=params,
    )
    return parse_obj_as(GuildScheduledEvent, await _request(adapter, bot, request))


async def _modify_guild_scheduled_event(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    event_id: SnowflakeType,
    **data,
) -> GuildScheduledEvent:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#modify-guild-scheduled-event"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    data = ModifyGuildScheduledEventParams.parse_obj(data).dict(exclude_unset=True)
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events/{event_id}",
        json=data,
    )
    return parse_obj_as(GuildScheduledEvent, await _request(adapter, bot, request))


async def _delete_guild_scheduled_event(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, event_id: SnowflakeType
) -> None:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#delete-guild-scheduled-event"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events/{event_id}",
    )
    await _request(adapter, bot, request)


async def _get_guild_scheduled_event_users(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    event_id: SnowflakeType,
    **params,
) -> List[GuildScheduledEventUser]:
    """https://discord.com/developers/docs/resources/guild-scheduled-event#get-guild-scheduled-event-users"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/scheduled-events/{event_id}/users",
        params=params,
    )
    return parse_obj_as(
        List[GuildScheduledEventUser], await _request(adapter, bot, request)
    )


async def _get_guild_template(
    adapter: "Adapter", bot: "Bot", template_code: str
) -> GuildTemplate:
    """https://discord.com/developers/docs/resources/guild-template#get-guild-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/templates/{template_code}",
    )
    return parse_obj_as(GuildTemplate, await _request(adapter, bot, request))


async def _create_guild_from_guild_template(
    adapter: "Adapter", bot: "Bot", template_code: str, **data
) -> Guild:
    """https://discord.com/developers/docs/resources/guild-template#create-guild-from-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/templates/{template_code}",
        json=data,
    )
    return parse_obj_as(Guild, await _request(adapter, bot, request))


async def _get_guild_templates(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[GuildTemplate]:
    """https://discord.com/developers/docs/resources/guild-template#get-guild-templates"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/templates",
    )
    return parse_obj_as(List[GuildTemplate], await _request(adapter, bot, request))


async def _create_guild_template(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, **data
) -> GuildTemplate:
    """https://discord.com/developers/docs/resources/guild-template#create-guild-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/templates",
        json=data,
    )
    return parse_obj_as(GuildTemplate, await _request(adapter, bot, request))


async def _sync_guild_template(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, template_code: str
) -> GuildTemplate:
    """https://discord.com/developers/docs/resources/guild-template#sync-guild-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PUT",
        url=adapter.base_url / f"guilds/{guild_id}/templates/{template_code}",
    )
    return parse_obj_as(GuildTemplate, await _request(adapter, bot, request))


async def _modify_guild_template(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, template_code: str, **data
) -> GuildTemplate:
    """https://discord.com/developers/docs/resources/guild-template#modify-guild-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/templates/{template_code}",
        json=data,
    )
    return parse_obj_as(GuildTemplate, await _request(adapter, bot, request))


async def _delete_guild_template(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, template_code: str
) -> None:
    """https://discord.com/developers/docs/resources/guild-template#delete-guild-template"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/templates/{template_code}",
    )
    await _request(adapter, bot, request)


async def _get_invite(
    adapter: "Adapter", bot: "Bot", invite_code: str, **params
) -> Invite:
    """https://discord.com/developers/docs/resources/invite#get-invite"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"invites/{invite_code}",
        params=params,
    )
    return parse_obj_as(Invite, await _request(adapter, bot, request))


async def _delete_invite(
    adapter: "Adapter", bot: "Bot", invite_code: str, reason: Optional[str] = None
) -> Invite:
    """https://discord.com/developers/docs/resources/invite#delete-invite"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"invites/{invite_code}",
    )
    return parse_obj_as(Invite, await _request(adapter, bot, request))


async def _create_stage_instance(
    adapter: "Adapter", bot: "Bot", **data
) -> StageInstance:
    """https://discord.com/developers/docs/resources/stage-instance#create-stage-instance"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / "stage-instances",
        json=data,
    )
    return parse_obj_as(StageInstance, await _request(adapter, bot, request))


async def _get_stage_instance(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
) -> Optional[StageInstance]:
    """https://discord.com/developers/docs/resources/stage-instance#get-stage-instance"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"stage-instances/{channel_id}",
    )
    return parse_obj_as(Optional[StageInstance], await _request(adapter, bot, request))


async def _modify_stage_instance(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> StageInstance:
    """https://discord.com/developers/docs/resources/stage-instance#modify-stage-instance"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"stage-instances/{channel_id}",
        json=data,
    )
    return parse_obj_as(StageInstance, await _request(adapter, bot, request))


async def _delete_stage_instance(
    adapter: "Adapter",
    bot: "Bot",
    channel_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/stage-instance#delete-stage-instance"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"stage-instances/{channel_id}",
    )
    await _request(adapter, bot, request)


async def _get_sticker(
    adapter: "Adapter", bot: "Bot", sticker_id: SnowflakeType
) -> Sticker:
    """https://discord.com/developers/docs/resources/sticker#get-sticker"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"stickers/{sticker_id}",
    )
    return parse_obj_as(Sticker, await _request(adapter, bot, request))


async def _list_nitro_sticker_packs(
    adapter: "Adapter", bot: "Bot"
) -> List[StickerPack]:
    """https://discord.com/developers/docs/resources/sticker#list-nitro-sticker-packs"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "sticker-packs",
    )
    return parse_obj_as(List[StickerPack], await _request(adapter, bot, request))


async def _list_guild_stickers(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Sticker]:
    """https://discord.com/developers/docs/resources/sticker#list-guild-stickers"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/stickers",
    )
    return parse_obj_as(List[Sticker], await _request(adapter, bot, request))


async def _get_guild_sticker(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType, sticker_id: SnowflakeType
) -> Sticker:
    """https://discord.com/developers/docs/resources/sticker#get-guild-sticker"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/stickers/{sticker_id}",
    )
    return parse_obj_as(Sticker, await _request(adapter, bot, request))


async def _create_guild_sticker(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    name: str,
    description: str,
    tags: str,
    file: File,
    reason: Optional[str] = None,
) -> Sticker:
    """https://discord.com/developers/docs/resources/sticker#create-guild-sticker"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    form = {
        "name": (None, name),
        "description": (None, description),
        "tags": (None, tags),
        "file": (file.filename, file.content),
    }
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        method="POST",
        url=adapter.base_url / f"guilds/{guild_id}/stickers",
        json={"name": name, "description": description, "tags": tags},
        files=form,
    )
    return parse_obj_as(Sticker, await _request(adapter, bot, request))


async def _modify_guild_sticker(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    sticker_id: SnowflakeType,
    **data,
) -> Sticker:
    """https://discord.com/developers/docs/resources/sticker#modify-guild-sticker"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"guilds/{guild_id}/stickers/{sticker_id}",
        json=data,
    )
    return parse_obj_as(Sticker, await _request(adapter, bot, request))


async def _delete_guild_sticker(
    adapter: "Adapter",
    bot: "Bot",
    guild_id: SnowflakeType,
    sticker_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/sticker#delete-guild-sticker"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"guilds/{guild_id}/stickers/{sticker_id}",
    )
    await _request(adapter, bot, request)


async def _get_current_user(adapter: "Adapter", bot: "Bot") -> User:
    """https://discord.com/developers/docs/resources/user#get-current-user"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "users/@me",
    )
    return parse_obj_as(User, await _request(adapter, bot, request))


async def _get_user(adapter: "Adapter", bot: "Bot", user_id: SnowflakeType) -> User:
    """https://discord.com/developers/docs/resources/user#get-user"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"users/{user_id}",
    )
    return parse_obj_as(User, await _request(adapter, bot, request))


async def _modify_current_user(adapter: "Adapter", bot: "Bot", **data) -> User:
    """https://discord.com/developers/docs/resources/user#modify-current-user"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / "users/@me",
        json=data,
    )
    return parse_obj_as(User, await _request(adapter, bot, request))


async def _get_current_user_guilds(
    adapter: "Adapter", bot: "Bot", **params
) -> List[CurrentUserGuild]:
    """https://discord.com/developers/docs/resources/user#get-current-user-guilds"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "users/@me/guilds",
        params=params,
    )
    return parse_obj_as(List[CurrentUserGuild], await _request(adapter, bot, request))


async def _get_current_user_guild_member(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> GuildMember:
    """https://discord.com/developers/docs/resources/user#get-current-user-guilds-member"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"users/@me/guilds/{guild_id}/member",
    )
    return parse_obj_as(GuildMember, await _request(adapter, bot, request))


async def _leave_guild(adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType) -> None:
    """https://discord.com/developers/docs/resources/user#leave-guild"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"users/@me/guilds/{guild_id}",
    )
    await _request(adapter, bot, request)


async def _create_DM(adapter: "Adapter", bot: "Bot", **data) -> Channel:
    """https://discord.com/developers/docs/resources/user#create-dm"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / "users/@me/channels",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _create_group_DM(adapter: "Adapter", bot: "Bot", **data) -> Channel:
    """https://discord.com/developers/docs/resources/user#create-group-dm"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / "users/@me/channels",
        json=data,
    )
    return parse_obj_as(Channel, await _request(adapter, bot, request))


async def _get_user_connections(
    adapter: "Adapter",
    bot: "Bot",
) -> List[Connection]:
    """https://discord.com/developers/docs/resources/user#get-user-connections"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "users/@me/connections",
    )
    return parse_obj_as(List[Connection], await _request(adapter, bot, request))


async def _get_user_application_role_connection(
    adapter: "Adapter", bot: "Bot", application_id: SnowflakeType
) -> ApplicationRoleConnection:
    """https://discord.com/developers/docs/resources/user#get-user-application-connections"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url
        / f"users/@me/applications/{application_id}/role-connection",
    )
    return parse_obj_as(
        ApplicationRoleConnection, await _request(adapter, bot, request)
    )


async def _update_user_application_role_connection(
    adapter: "Adapter", bot: "Bot", application_id: SnowflakeType, **data
) -> ApplicationRoleConnection:
    """https://discord.com/developers/docs/resources/user#modify-current-user"""
    if "metadata" in data and isinstance(
        data["metadata"], ApplicationRoleConnectionMetadata
    ):
        data["metadata"] = data["metadata"].dict(exclude_unset=True)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url
        / f"users/@me/applications/{application_id}/role-connection",
        json=data,
    )
    return parse_obj_as(
        ApplicationRoleConnection, await _request(adapter, bot, request)
    )


async def _list_voice_regions(adapter: "Adapter", bot: "Bot") -> List[VoiceRegion]:
    """https://discord.com/developers/docs/resources/voice#list-voice-regions"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "voice/regions",
    )
    return parse_obj_as(List[VoiceRegion], await _request(adapter, bot, request))


async def _create_webhook(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType, **data
) -> Webhook:
    """https://discord.com/developers/docs/resources/webhook#create-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"channels/{channel_id}/webhooks",
        json=data,
    )
    return parse_obj_as(Webhook, await _request(adapter, bot, request))


async def _get_channel_webhooks(
    adapter: "Adapter", bot: "Bot", channel_id: SnowflakeType
) -> List[Webhook]:
    """https://discord.com/developers/docs/resources/webhook#get-channel-webhooks"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"channels/{channel_id}/webhooks",
    )
    return parse_obj_as(List[Webhook], await _request(adapter, bot, request))


async def _get_guild_webhooks(
    adapter: "Adapter", bot: "Bot", guild_id: SnowflakeType
) -> List[Webhook]:
    """https://discord.com/developers/docs/resources/webhook#get-guild-webhooks"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"guilds/{guild_id}/webhooks",
    )
    return parse_obj_as(List[Webhook], await _request(adapter, bot, request))


async def _get_webhook(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType
) -> Webhook:
    """https://discord.com/developers/docs/resources/webhook#get-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"webhooks/{webhook_id}",
    )
    return parse_obj_as(Webhook, await _request(adapter, bot, request))


async def _get_webhook_with_token(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str
) -> Webhook:
    """https://discord.com/developers/docs/resources/webhook#get-webhook-with-token"""
    request = Request(
        method="GET",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}",
    )
    return parse_obj_as(Webhook, await _request(adapter, bot, request))


async def _modify_webhook(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, **data
) -> Webhook:
    """https://discord.com/developers/docs/resources/webhook#modify-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason := data.pop("reason"):
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / f"webhooks/{webhook_id}",
        json=data,
    )
    return parse_obj_as(Webhook, await _request(adapter, bot, request))


async def _modify_webhook_with_token(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str, **data
) -> Webhook:
    """https://discord.com/developers/docs/resources/webhook#modify-webhook-with-token"""
    request = Request(
        method="PATCH",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}",
        json=data,
    )
    return parse_obj_as(Webhook, await _request(adapter, bot, request))


async def _delete_webhook(
    adapter: "Adapter",
    bot: "Bot",
    webhook_id: SnowflakeType,
    reason: Optional[str] = None,
) -> None:
    """https://discord.com/developers/docs/resources/webhook#delete-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    if reason:
        headers["X-Audit-Log-Reason"] = reason
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"webhooks/{webhook_id}",
    )
    await _request(adapter, bot, request)


async def _delete_webhook_with_token(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str
) -> None:
    """https://discord.com/developers/docs/resources/webhook#delete-webhook-with-token"""
    request = Request(
        method="DELETE",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}",
    )
    await _request(adapter, bot, request)


async def _execute_webhook(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str, **data
) -> None:
    """https://discord.com/developers/docs/resources/webhook#execute-webhook"""
    params = {}
    if wait := data.pop("wait"):
        params["wait"] = wait
    if thread_id := data.pop("thread_id"):
        params["thread_id"] = thread_id
    data = parse_data(data, ExecuteWebhookParams)
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}",
        params=params,
        **data,
    )
    await _request(adapter, bot, request)


async def _execute_slack_compatible_webhook(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str, **params
) -> None:
    """https://discord.com/developers/docs/resources/webhook#execute-slackcompatible-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}/slack",
        params=params,
    )
    await _request(adapter, bot, request)


async def _execute_github_compatible_webhook(
    adapter: "Adapter", bot: "Bot", webhook_id: SnowflakeType, token: str, **params
) -> None:
    """https://discord.com/developers/docs/resources/webhook#execute-githubcompatible-webhook"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="POST",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}/github",
        params=params,
    )
    await _request(adapter, bot, request)


async def _get_webhook_message(
    adapter: "Adapter",
    bot: "Bot",
    webhook_id: SnowflakeType,
    token: str,
    message_id: SnowflakeType,
    **params,
) -> MessageGet:
    """https://discord.com/developers/docs/resources/webhook#get-webhook-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}/messages/{message_id}",
        params=params,
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _edit_webhook_message(adapter: "Adapter", bot: "Bot", **data) -> MessageGet:
    """https://discord.com/developers/docs/resources/webhook#edit-webhook-message"""
    params = {}
    if thread_id := data.pop("thread_id"):
        params["thread_id"] = thread_id
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    data = parse_data(data, ExecuteWebhookParams)
    request = Request(
        headers=headers,
        method="PATCH",
        url=adapter.base_url / "webhooks/@me/messages",
        params=params,
        **data,
    )
    return parse_obj_as(MessageGet, await _request(adapter, bot, request))


async def _delete_webhook_message(
    adapter: "Adapter",
    bot: "Bot",
    webhook_id: SnowflakeType,
    token: str,
    message_id: SnowflakeType,
    **params,
) -> None:
    """https://discord.com/developers/docs/resources/webhook#delete-webhook-message"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="DELETE",
        url=adapter.base_url / f"webhooks/{webhook_id}/{token}/messages/{message_id}",
        params=params,
    )
    await _request(adapter, bot, request)


async def _get_gateway(adapter: "Adapter", bot: "Bot") -> Gateway:
    """https://discord.com/developers/docs/topics/gateway#get-gateway"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "gateway",
    )
    return parse_obj_as(Gateway, await _request(adapter, bot, request))


async def _get_gateway_bot(adapter: "Adapter", bot: "Bot") -> GatewayBot:
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "gateway/bot",
    )
    return parse_obj_as(GatewayBot, await _request(adapter, bot, request))


async def _get_current_bot_application_information(
    adapter: "Adapter", bot: "Bot"
) -> Application:
    """https://discord.com/developers/docs/resources/user#get-current-application-information"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "oauth2/applications/@me",
    )
    return parse_obj_as(Application, await _request(adapter, bot, request))


async def _get_current_authorization_information(
    adapter: "Adapter", bot: "Bot"
) -> AuthorizationResponse:
    """https://discord.com/developers/docs/resources/user#get-current-authorization-information"""
    headers = {"Authorization": adapter.get_authorization(bot.bot_info)}
    request = Request(
        headers=headers,
        method="GET",
        url=adapter.base_url / "oauth2/@me",
    )
    return parse_obj_as(AuthorizationResponse, await _request(adapter, bot, request))


API_HANDLERS = {
    "get_application_role_connection_metadata_records": _get_application_role_connection_metadata_records,
    "update_application_role_connection_metadata_records": _update_application_role_connection_metadata_records,
    "get_guild_audit_log": _get_guild_audit_log,
    "list_auto_moderation_rules_for_guild": _list_auto_moderation_rules_for_guild,
    "get_auto_moderation_rule": _get_auto_moderation_rule,
    "create_auto_moderation_rule": _create_auto_moderation_rule,
    "modify_auto_moderation_rule": _modify_auto_moderation_rule,
    "delete_auto_moderation_rule": _delete_auto_moderation_rule,
    "get_channel": _get_channel,
    "modify_DM": _modify_DM,
    "modify_channel": _modify_channel,
    "modify_thread": _modify_thread,
    "delete_channel": _delete_channel,
    "get_channel_messages": _get_channel_messages,
    "get_channel_message": _get_channel_message,
    "create_message": _create_message,
    "crosspost_message": _crosspost_message,
    "create_reaction": _create_reaction,
    "delete_own_reaction": _delete_own_reaction,
    "delete_user_reaction": _delete_user_reaction,
    "get_reactions": _get_reactions,
    "delete_all_reactions": _delete_all_reactions,
    "delete_all_reactions_for_emoji": _delete_all_reactions_for_emoji,
    "edit_message": _edit_message,
    "delete_message": _delete_message,
    "bulk_delete_message": _bulk_delete_message,
    "edit_channel_permissions": _edit_channel_permissions,
    "get_channel_invites": _get_channel_invites,
    "create_channel_invite": _create_channel_invite,
    "delete_channel_permission": _delete_channel_permission,
    "follow_announcement_channel": _follow_announcement_channel,
    "trigger_typing_indicator": _trigger_typing_indicator,
    "get_pinned_messages": _get_pinned_messages,
    "pin_message": _pin_message,
    "unpin_message": _unpin_message,
    "group_DM_add_recipient": _group_DM_add_recipient,
    "group_DM_remove_recipient": _group_DM_remove_recipient,
    "start_thread_from_message": _start_thread_from_message,
    "start_thread_without_message": _start_thread_without_message,
    "start_thread_in_forum_channel": _start_thread_in_forum_channel,
    "join_thread": _join_thread,
    "add_thread_member": _add_thread_member,
    "leave_thread": _leave_thread,
    "remove_thread_member": _remove_thread_member,
    "get_thread_member": _get_thread_member,
    "list_thread_members": _list_thread_members,
    "list_public_archived_threads": _list_public_archived_threads,
    "list_private_archived_threads": _list_private_archived_threads,
    "list_joined_private_archived_threads": _list_joined_private_archived_threads,
    "list_guild_emojis": _list_guild_emojis,
    "get_guild_emoji": _get_guild_emoji,
    "create_guild_emoji": _create_guild_emoji,
    "modify_guild_emoji": _modify_guild_emoji,
    "delete_guild_emoji": _delete_guild_emoji,
    "create_guild": _create_guild,
    "get_guild": _get_guild,
    "get_guild_preview": _get_guild_preview,
    "modify_guild": _modify_guild,
    "delete_guild": _delete_guild,
    "get_guild_channels": _get_guild_channels,
    "create_guild_channel": _create_guild_channel,
    "modify_guild_channel_positions": _modify_guild_channel_positions,
    "list_active_guild_threads": _list_active_guild_threads,
    "get_guild_member": _get_guild_member,
    "list_guild_members": _list_guild_members,
    "search_guild_members": _search_guild_members,
    "add_guild_member": _add_guild_member,
    "modify_guild_member": _modify_guild_member,
    "modify_current_member": _modify_current_member,
    "modify_current_user_nick": _modify_current_user_nick,
    "add_guild_member_role": _add_guild_member_role,
    "remove_guild_member_role": _remove_guild_member_role,
    "remove_guild_member": _remove_guild_member,
    "get_guild_bans": _get_guild_bans,
    "get_guild_ban": _get_guild_ban,
    "create_guild_ban": _create_guild_ban,
    "remove_guild_ban": _remove_guild_ban,
    "get_guild_roles": _get_guild_roles,
    "create_guild_role": _create_guild_role,
    "modify_guild_role_positions": _modify_guild_role_positions,
    "modify_guild_role": _modify_guild_role,
    "modify_guild_MFA_level": _modify_guild_MFA_level,
    "delete_guild_role": _delete_guild_role,
    "get_guild_prune_count": _get_guild_prune_count,
    "begin_guild_prune": _begin_guild_prune,
    "get_guild_voice_regions": _get_guild_voice_regions,
    "get_guild_invites": _get_guild_invites,
    "get_guild_integrations": _get_guild_integrations,
    "delete_guild_integration": _delete_guild_integration,
    "get_guild_widget_settings": _get_guild_widget_settings,
    "modify_guild_widget": _modify_guild_widget,
    "get_guild_widget": _get_guild_widget,
    "get_guild_vanity_url": _get_guild_vanity_url,
    "get_guild_widget_image": _get_guild_widget_image,
    "get_guild_welcome_screen": _get_guild_welcome_screen,
    "modify_guild_welcome_screen": _modify_guild_welcome_screen,
    "get_guild_onboarding": _get_guild_onboarding,
    "modify_current_user_voice_state": _modify_current_user_voice_state,
    "modify_user_voice_state": _modify_user_voice_state,
    "list_scheduled_events_for_guild": _list_scheduled_events_for_guild,
    "create_guild_schedule_event": _create_guild_schedule_event,
    "get_guild_scheduled_event": _get_guild_scheduled_event,
    "modify_guild_scheduled_event": _modify_guild_scheduled_event,
    "delete_guild_scheduled_event": _delete_guild_scheduled_event,
    "get_guild_scheduled_event_users": _get_guild_scheduled_event_users,
    "get_guild_template": _get_guild_template,
    "create_guild_from_guild_template": _create_guild_from_guild_template,
    "get_guild_templates": _get_guild_templates,
    "create_guild_template": _create_guild_template,
    "sync_guild_template": _sync_guild_template,
    "modify_guild_template": _modify_guild_template,
    "delete_guild_template": _delete_guild_template,
    "get_invite": _get_invite,
    "delete_invite": _delete_invite,
    "create_stage_instance": _create_stage_instance,
    "get_stage_instance": _get_stage_instance,
    "modify_stage_instance": _modify_stage_instance,
    "delete_stage_instance": _delete_stage_instance,
    "get_sticker": _get_sticker,
    "list_nitro_sticker_packs": _list_nitro_sticker_packs,
    "list_guild_stickers": _list_guild_stickers,
    "get_guild_sticker": _get_guild_sticker,
    "create_guild_sticker": _create_guild_sticker,
    "modify_guild_sticker": _modify_guild_sticker,
    "delete_guild_sticker": _delete_guild_sticker,
    "get_current_user": _get_current_user,
    "get_user": _get_user,
    "modify_current_user": _modify_current_user,
    "get_current_user_guilds": _get_current_user_guilds,
    "get_current_user_guild_member": _get_current_user_guild_member,
    "leave_guild": _leave_guild,
    "create_DM": _create_DM,
    "create_group_DM": _create_group_DM,
    "get_user_connections": _get_user_connections,
    "get_user_application_role_connection": _get_user_application_role_connection,
    "update_user_application_role_connection": _update_user_application_role_connection,
    "list_voice_regions": _list_voice_regions,
    "create_webhook": _create_webhook,
    "get_channel_webhooks": _get_channel_webhooks,
    "get_guild_webhooks": _get_guild_webhooks,
    "get_webhook": _get_webhook,
    "get_webhook_with_token": _get_webhook_with_token,
    "modify_webhook": _modify_webhook,
    "modify_webhook_with_token": _modify_webhook_with_token,
    "delete_webhook": _delete_webhook,
    "delete_webhook_with_token": _delete_webhook_with_token,
    "execute_webhook": _execute_webhook,
    "execute_slack_compatible_webhook": _execute_slack_compatible_webhook,
    "execute_github_compatible_webhook": _execute_github_compatible_webhook,
    "get_webhook_message": _get_webhook_message,
    "edit_webhook_message": _edit_webhook_message,
    "delete_webhook_message": _delete_webhook_message,
    "get_gateway": _get_gateway,
    "get_gateway_bot": _get_gateway_bot,
    "get_current_bot_application_information": _get_current_bot_application_information,
    "get_current_authorization_information": _get_current_authorization_information,
}
