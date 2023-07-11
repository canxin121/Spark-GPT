import datetime
from typing import Dict, List, Union, Literal, Optional

from .model import *
from .types import *

class ApiClient:
    async def get_application_role_connection_metadata_records(
        self, *, application_id: SnowflakeType
    ) -> List[ApplicationRoleConnectionMetadata]:
        """get application role connection metadata records

        see https://discord.com/developers/docs/resources/application-role-connection-metadata#get-application-role-connection-metadata-records
        """
        ...
    async def update_application_role_connection_metadata_records(
        self, *, application_id: SnowflakeType
    ) -> List[ApplicationRoleConnectionMetadata]:
        """get application role connection metadata records

        see https://discord.com/developers/docs/resources/application-role-connection-metadata#get-application-role-connection-metadata-records
        """
        ...
    async def get_guild_audit_log(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: Optional[SnowflakeType] = ...,
        action_type: Optional[AuditLogEventType] = ...,
        before: Optional[SnowflakeType] = ...,
        after: Optional[SnowflakeType] = ...,
        limit: Optional[int] = ...,
    ) -> AuditLog:
        """get guild audit log

        see https://discord.com/developers/docs/resources/audit-log#get-guild-audit-log
        """
        ...
    async def list_auto_moderation_rules_for_guild(
        self, *, guild_id: SnowflakeType
    ) -> List[AutoModerationRule]:
        """list auto moderation rules for guild

        see https://discord.com/developers/docs/resources/auto-moderation#list-auto-moderation-rules-for-guild
        """
        ...
    async def get_auto_moderation_rule(
        self, *, guild_id: SnowflakeType, rule_id: SnowflakeType
    ) -> AutoModerationRule:
        """get auto moderation rule

        see https://discord.com/developers/docs/resources/auto-moderation#get-auto-moderation-rule
        """
        ...
    async def create_auto_moderation_rule(
        self, *, guild_id: SnowflakeType, **data
    ) -> AutoModerationRule:
        """create auto moderation rule

        see https://discord.com/developers/docs/resources/auto-moderation#create-auto-moderation-rule
        """
        ...
    async def modify_auto_moderation_rule(
        self,
        *,
        guild_id: SnowflakeType,
        rule_id: SnowflakeType,
        name: str,
        event_type: AutoModerationRuleEventType,
        trigger_type: TriggerType,
        trigger_metadata: Optional[TriggerMetadata] = ...,
        actions: List[AutoModerationAction] = ...,
        enabled: Optional[bool] = ...,
        exempt_roles: List[SnowflakeType] = ...,
        exempt_channels: List[SnowflakeType] = ...,
        reason: Optional[str] = ...,
    ) -> AutoModerationRule:
        """modify auto moderation rule

        see https://discord.com/developers/docs/resources/auto-moderation#modify-auto-moderation-rule
        """
        ...
    async def delete_auto_moderation_rule(
        self,
        *,
        guild_id: SnowflakeType,
        rule_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """delete auto moderation rule

        see https://discord.com/developers/docs/resources/auto-moderation#delete-auto-moderation-rule
        """
        ...
    async def get_channel(self, *, channel_id: SnowflakeType) -> Channel:
        """get channel

        see https://discord.com/developers/docs/resources/channel#get-channel"""
        ...
    async def modify_DM(
        self,
        *,
        channel_id: SnowflakeType,
        name: str = ...,
        icon: bytes = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """modify DM

        see https://discord.com/developers/docs/resources/channel#modify-channel-json-params-group-dm
        """
        ...
    async def modify_channel(
        self,
        *,
        channel_id: SnowflakeType,
        name: Optional[str] = ...,
        type: Optional[ChannelType] = ...,
        position: Optional[int] = ...,
        topic: Optional[str] = ...,
        nsfw: Optional[bool] = ...,
        rate_limit_per_user: Optional[int] = ...,
        bitrate: Optional[int] = ...,
        user_limit: Optional[int] = ...,
        permission_overwrites: Optional[List[Overwrite]] = ...,
        parent_id: Optional[SnowflakeType] = ...,
        rtc_region: Optional[str] = ...,
        video_quality_mode: Optional[VideoQualityMode] = ...,
        default_auto_archive_duration: Optional[int] = ...,
        flags: Optional[ChannelFlags] = ...,
        available_tags: Optional[List[ForumTag]] = ...,
        default_reaction_emoji: Optional[DefaultReaction] = ...,
        default_thread_rate_limit_per_user: Optional[int] = ...,
        default_sort_order: Optional[SortOrderTypes] = ...,
        default_forum_layout: Optional[ForumLayoutTypes] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """modify channel

        see https://discord.com/developers/docs/resources/channel#modify-channel-json-params-guild-channel
        """
        ...
    async def modify_thread(
        self,
        *,
        channel_id: SnowflakeType,
        name: str = ...,
        archived: bool = ...,
        auto_archive_duration: int = ...,
        locked: bool = ...,
        invitable: bool = ...,
        rate_limit_per_user: Optional[int] = ...,
        flags: Optional[ChannelFlags] = ...,
        applied_tags: Optional[List[SnowflakeType]] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """modify thread

        see https://discord.com/developers/docs/resources/channel#modify-channel-json-params-thread
        """
        ...
    async def delete_channel(
        self, *, channel_id: SnowflakeType, reason: Optional[str] = ...
    ) -> Channel:
        """delete channel

        see https://discord.com/developers/docs/resources/channel#deleteclose-channel"""
        ...
    async def get_channel_messages(
        self,
        *,
        channel_id: SnowflakeType,
        around: Optional[SnowflakeType] = ...,
        before: Optional[SnowflakeType] = ...,
        after: Optional[SnowflakeType] = ...,
        limit: Optional[int] = ...,
    ) -> List[MessageGet]:
        """get channel messages

        see https://discord.com/developers/docs/resources/channel#get-channel-messages
        """
        ...
    async def get_channel_message(
        self, *, channel_id: SnowflakeType, message_id: SnowflakeType
    ) -> MessageGet:
        """get channel message

        see https://discord.com/developers/docs/resources/channel#get-channel-message"""
        ...
    async def create_message(
        self,
        *,
        channel_id: SnowflakeType,
        content: Optional[str] = ...,
        nonce: Optional[Union[int, str]] = ...,
        tts: Optional[bool] = ...,
        embeds: Optional[List[Embed]] = ...,
        allowed_mentions: Optional[AllowedMention] = ...,
        message_reference: Optional[MessageReference] = ...,
        components: Optional[List[DirectComponent]] = ...,
        sticker_ids: Optional[List[SnowflakeType]] = ...,
        files: Optional[List[File]] = ...,
        attachments: Optional[List[AttachmentSend]] = ...,
        flags: Optional[MessageFlag] = ...,
    ) -> MessageGet:
        """create message

        see https://discord.com/developers/docs/resources/channel#create-message
        """
        ...
    async def crosspost_message(
        self, *, channel_id: SnowflakeType, message_id: SnowflakeType
    ) -> MessageGet:
        """crosspost message

        see https://discord.com/developers/docs/resources/channel#crosspost-message"""
        ...
    async def create_reaction(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        emoji: str,
        emoji_id: Optional[SnowflakeType] = None,
    ) -> None:
        """create reaction

        see https://discord.com/developers/docs/resources/channel#create-reaction"""
        ...
    async def delete_own_reaction(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        emoji: str,
        emoji_id: Optional[SnowflakeType] = None,
    ) -> None:
        """delete own reaction

        see https://discord.com/developers/docs/resources/channel#delete-own-reaction"""
        ...
    async def delete_user_reaction(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        user_id: SnowflakeType,
        emoji: str,
        emoji_id: Optional[SnowflakeType] = None,
    ) -> None:
        """delete user reaction

        see https://discord.com/developers/docs/resources/channel#delete-user-reaction
        """
        ...
    async def get_reactions(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        emoji: str,
        emoji_id: Optional[SnowflakeType] = None,
        after: Optional[SnowflakeType] = ...,
        limit: Optional[int] = ...,
    ) -> List[User]:
        """get reactions

        see https://discord.com/developers/docs/resources/channel#get-reactions"""
        ...
    async def delete_all_reactions(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
    ) -> None:
        """

        see https://discord.com/developers/docs/resources/channel#delete-all-reactions
        """
        ...
    async def delete_all_reactions_for_emoji(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        emoji: str,
        emoji_id: Optional[SnowflakeType] = None,
    ) -> None:
        """

        see https://discord.com/developers/docs/resources/channel#delete-all-reactions
        """
        ...
    async def edit_message(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        content: Optional[str] = ...,
        embeds: Optional[List[Embed]] = ...,
        flags: Optional[MessageFlag] = ...,
        allowed_mentions: Optional[AllowedMention] = ...,
        components: Optional[List[DirectComponent]] = ...,
        files: Optional[List[File]] = ...,
        attachments: Optional[List[AttachmentSend]] = ...,
    ) -> MessageGet:
        """see https://discord.com/developers/docs/resources/channel#edit-message"""
        ...
    async def delete_message(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#delete-message"""
        ...
    async def bulk_delete_message(
        self,
        *,
        channel_id: SnowflakeType,
        messages: List[SnowflakeType],
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#bulk-delete-messages"""
        ...
    async def edit_channel_permissions(
        self,
        *,
        channel_id: SnowflakeType,
        overwrite_id: SnowflakeType,
        allow: Optional[str] = ...,
        deny: Optional[str] = ...,
        type: Optional[OverwriteType] = ...,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#edit-channel-permissions"""
        ...
    async def get_channel_invites(self, *, channel_id: SnowflakeType) -> List[Invite]:
        """https://discord.com/developers/docs/resources/channel#get-channel-invites"""
        ...
    async def create_channel_invite(
        self,
        *,
        channel_id: SnowflakeType,
        max_age: Optional[int] = ...,
        max_uses: Optional[int] = ...,
        temporary: Optional[bool] = ...,
        unique: Optional[bool] = ...,
        target_type: Optional[int] = ...,
        target_user_id: Optional[SnowflakeType] = ...,
        target_application_id: Optional[SnowflakeType] = ...,
        reason: Optional[str] = ...,
    ) -> Invite:
        """https://discord.com/developers/docs/resources/channel#create-channel-invite"""
        ...
    async def delete_channel_permission(
        self,
        *,
        channel_id: SnowflakeType,
        overwrite_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#delete-channel-permission"""
        ...
    async def follow_announcement_channel(
        self, *, channel_id: SnowflakeType, webhook_channel_id: SnowflakeType = ...
    ) -> FollowedChannel:
        """https://discord.com/developers/docs/resources/channel#follow-news-channel"""
        ...
    async def trigger_typing_indicator(self, *, channel_id: SnowflakeType) -> None:
        """https://discord.com/developers/docs/resources/channel#trigger-typing-indicator"""
        ...
    async def get_pinned_messages(self, *, channel_id: SnowflakeType) -> List[MessageGet]:
        """https://discord.com/developers/docs/resources/channel#get-pinned-messages"""
        ...
    async def pin_message(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#add-pinned-channel-message"""
        ...
    async def unpin_message(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#delete-pinned-channel-message"""
        ...
    async def group_DM_add_recipient(
        self,
        *,
        channel_id: SnowflakeType,
        user_id: SnowflakeType,
        access_token: str = ...,
        nick: str = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#group-dm-add-recipient"""
        ...
    async def group_DM_remove_recipient(
        self, *, channel_id: SnowflakeType, user_id: SnowflakeType
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#group-dm-remove-recipient"""
        ...
    async def start_thread_from_message(
        self,
        *,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        name: str = ...,
        auto_archive_duration: Optional[int] = ...,
        rate_limit_per_user: Optional[int] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """https://discord.com/developers/docs/resources/channel#start-thread-with-message"""
        ...
    async def start_thread_without_message(
        self,
        *,
        channel_id: SnowflakeType,
        name: str = ...,
        auto_archive_duration: Optional[int] = ...,
        type: Optional[ChannelType] = ...,
        invitable: Optional[bool] = ...,
        rate_limit_per_user: Optional[int] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """https://discord.com/developers/docs/resources/channel#start-thread-without-message"""
        ...

        # TODO: Returns a channel, with a nested message object, on success
    async def start_thread_in_forum_channel(
        self,
        *,
        channel_id: SnowflakeType,
        name: str = ...,
        auto_archive_duration: Optional[int] = ...,
        rate_limit_per_user: Optional[int] = ...,
        applied_tags: Optional[List[SnowflakeType]] = ...,
        content: Optional[str] = ...,
        embeds: Optional[List[Embed]] = ...,
        allowed_mentions: Optional[AllowedMention] = ...,
        components: Optional[List[DirectComponent]] = ...,
        sticker_ids: Optional[List[SnowflakeType]] = ...,
        files: Optional[List[File]] = ...,
        attachments: Optional[List[AttachmentSend]] = ...,
        flags: Optional[MessageFlag] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """https://discord.com/developers/docs/resources/channel#start-thread-in-forum-channel"""
        ...
    async def join_thread(self, *, channel_id: SnowflakeType) -> None:
        """https://discord.com/developers/docs/resources/channel#join-thread"""
        ...
    async def add_thread_member(
        self, *, channel_id: SnowflakeType, user_id: SnowflakeType
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#add-thread-member"""
        ...
    async def leave_thread(self, *, channel_id: SnowflakeType) -> None:
        """https://discord.com/developers/docs/resources/channel#leave-thread"""
        ...
    async def remove_thread_member(
        self, *, channel_id: SnowflakeType, user_id: SnowflakeType
    ) -> None:
        """https://discord.com/developers/docs/resources/channel#remove-thread-member"""
        ...
    async def get_thread_member(
        self,
        *,
        channel_id: SnowflakeType,
        user_id: SnowflakeType,
        with_member: Optional[bool] = ...,
    ) -> ThreadMember:
        """https://discord.com/developers/docs/resources/channel#get-thread-member"""
        ...
    async def list_thread_members(
        self,
        *,
        channel_id: SnowflakeType,
        with_member: Optional[bool] = ...,
        after: Optional[SnowflakeType] = ...,
        limit: Optional[int] = ...,
    ) -> List[ThreadMember]:
        """https://discord.com/developers/docs/resources/channel#list-thread-members"""
        ...
    async def list_public_archived_threads(
        self,
        *,
        channel_id: SnowflakeType,
        before: Optional[datetime.datetime] = ...,
        limit: Optional[int] = ...,
    ) -> ArchivedThreadsResponse:
        """https://discord.com/developers/docs/resources/channel#list-public-archived-threads"""
        ...
    async def list_private_archived_threads(
        self,
        *,
        channel_id: SnowflakeType,
        before: Optional[datetime.datetime] = ...,
        limit: Optional[int] = ...,
    ) -> ArchivedThreadsResponse:
        """https://discord.com/developers/docs/resources/channel#list-private-archived-threads"""
        ...
    async def list_joined_private_archived_threads(
        self,
        *,
        channel_id: SnowflakeType,
        before: Optional[datetime.datetime] = ...,
        limit: Optional[int] = ...,
    ) -> ArchivedThreadsResponse:
        """https://discord.com/developers/docs/resources/channel#list-joined-private-archived-threads"""
        ...
    async def list_guild_emojis(self, *, guild_id: SnowflakeType) -> List[Emoji]:
        """https://discord.com/developers/docs/resources/emoji#list-guild-emojis"""
        ...
    async def get_guild_emoji(
        self, *, guild_id: SnowflakeType, emoji_id: SnowflakeType
    ) -> Emoji:
        """https://discord.com/developers/docs/resources/emoji#get-guild-emoji"""
        ...
    async def create_guild_emoji(
        self,
        *,
        guild_id: SnowflakeType,
        name: str = ...,
        image: str = ...,
        roles: List[SnowflakeType] = ...,
        reason: Optional[str] = ...,
    ) -> Emoji:
        """https://discord.com/developers/docs/resources/emoji#create-guild-emoji"""
        ...
    async def modify_guild_emoji(
        self,
        *,
        guild_id: SnowflakeType,
        emoji_id: str,
        name: str = ...,
        roles: Optional[List[SnowflakeType]] = ...,
        reason: Optional[str] = ...,
    ) -> Emoji:
        """https://discord.com/developers/docs/resources/emoji#modify-guild-emoji"""
        ...
    async def delete_guild_emoji(
        self, *, guild_id: SnowflakeType, emoji_id: str, reason: Optional[str] = ...
    ) -> None:
        """https://discord.com/developers/docs/resources/emoji#delete-guild-emoji"""
        ...
    async def create_guild(
        self,
        *,
        name: str = ...,
        region: Optional[str] = ...,
        icon: Optional[str] = ...,
        verification_level: Optional[VerificationLevel] = ...,
        default_message_notifications: Optional[DefaultMessageNotificationLevel] = ...,
        explicit_content_filter: Optional[ExplicitContentFilterLevel] = ...,
        roles: Optional[List["Role"]] = ...,
        channels: Optional[List[Channel]] = ...,
        afk_channel_id: Optional[Snowflake] = ...,
        afk_timeout: Optional[int] = ...,
        system_channel_id: Optional[Snowflake] = ...,
        system_channel_flags: Optional[SystemChannelFlags] = ...,
    ) -> Guild:
        """https://discord.com/developers/docs/resources/guild#create-guild"""
        ...
    async def get_guild(
        self, *, guild_id: SnowflakeType, with_counts: Optional[bool] = ...
    ) -> Guild:
        """https://discord.com/developers/docs/resources/guild#get-guild"""
        ...
    async def get_guild_preview(self, *, guild_id: SnowflakeType) -> GuildPreview:
        """https://discord.com/developers/docs/resources/guild#get-guild-preview"""
        ...
    async def modify_guild(
        self,
        *,
        guild_id: SnowflakeType,
        name: str = ...,
        region: Optional[str] = ...,
        verification_level: Optional[VerificationLevel] = ...,
        default_message_notifications: Optional[DefaultMessageNotificationLevel] = ...,
        explicit_content_filter: Optional[ExplicitContentFilterLevel] = ...,
        afk_channel_id: Optional[Snowflake] = ...,
        afk_timeout: Optional[int] = ...,
        icon: Optional[str] = ...,
        owner_id: Optional[Snowflake] = ...,
        splash: Optional[str] = ...,
        discovery_splash: Optional[str] = ...,
        banner: Optional[str] = ...,
        system_channel_id: Optional[Snowflake] = ...,
        system_channel_flags: Optional[SystemChannelFlags] = ...,
        rules_channel_id: Optional[Snowflake] = ...,
        public_updates_channel_id: Optional[Snowflake] = ...,
        preferred_locale: Optional[str] = ...,
        features: Optional[List[GuildFeature]] = ...,
        description: Optional[str] = ...,
        premium_progress_bar_enabled: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> Guild:
        """https://discord.com/developers/docs/resources/guild#modify-guild"""
        ...
    async def delete_guild(self, *, guild_id: SnowflakeType) -> None:
        """https://discord.com/developers/docs/resources/guild#delete-guild"""
        ...
    async def get_guild_channels(self, *, guild_id: SnowflakeType) -> List[Channel]:
        """https://discord.com/developers/docs/resources/guild#get-guild-channels"""
        ...
    async def create_guild_channel(
        self,
        *,
        guild_id: SnowflakeType,
        name: str = ...,
        type: Optional[ChannelType] = ...,
        topic: Optional[str] = ...,
        bitrate: Optional[int] = ...,
        user_limit: Optional[int] = ...,
        rate_limit_per_user: Optional[int] = ...,
        position: Optional[int] = ...,
        permission_overwrites: Optional[List["Overwrite"]] = ...,
        parent_id: Optional[Snowflake] = ...,
        nsfw: Optional[bool] = ...,
        rtc_region: Optional[str] = ...,
        video_quality_mode: Optional[VideoQualityMode] = ...,
        default_auto_archive_duration: Optional[int] = ...,
        default_reaction_emoji: Optional[DefaultReaction] = ...,
        available_tags: Optional[List[ForumTag]] = ...,
        default_sort_order: Optional[SortOrderTypes] = ...,
        reason: Optional[str] = ...,
    ) -> Channel:
        """https://discord.com/developers/docs/resources/guild#create-guild-channel"""
        ...
    async def modify_guild_channel_positions(
        self,
        *,
        guild_id: SnowflakeType,
        id: SnowflakeType = ...,
        position: Optional[int] = ...,
        lock_permissions: Optional[bool] = ...,
        parent_id: Optional[SnowflakeType] = ...,
    ) -> Guild:
        """https://discord.com/developers/docs/resources/guild#modify-guild-channel-positions"""
        ...
    async def list_active_guild_threads(
        self, *, guild_id: SnowflakeType
    ) -> ListActiveGuildThreadsResponse:
        """https://discord.com/developers/docs/resources/guild#list-active-guild-threads"""
        ...
    async def get_guild_member(
        self, *, guild_id: SnowflakeType, user_id: SnowflakeType
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/guild#get-guild-member"""
        ...
    async def list_guild_members(
        self,
        *,
        guild_id: SnowflakeType,
        limit: Optional[int] = ...,
        after: Optional[SnowflakeType] = ...,
    ) -> List[GuildMember]:
        """https://discord.com/developers/docs/resources/guild#list-guild-members"""
        ...
    async def search_guild_members(
        self,
        *,
        guild_id: SnowflakeType,
        query: Optional[str] = ...,
        limit: Optional[int] = ...,
    ) -> List[GuildMember]:
        """https://discord.com/developers/docs/resources/guild#search-guild-members"""
        ...
    async def add_guild_member(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        access_token: str = ...,
        nick: Optional[str] = ...,
        roles: Optional[List[SnowflakeType]] = ...,
        mute: Optional[bool] = ...,
        deaf: Optional[bool] = ...,
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/guild#add-guild-member"""
        ...
    async def modify_guild_member(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        nick: Optional[str] = ...,
        roles: Optional[List[SnowflakeType]] = ...,
        mute: Optional[bool] = ...,
        deaf: Optional[bool] = ...,
        channel_id: Optional[SnowflakeType] = ...,
        communication_disabled_until: Optional[datetime.datetime] = ...,
        flags: Optional[GuildMemberFlags] = ...,
        reason: Optional[str] = ...,
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/guild#modify-guild-member"""
        ...
    async def modify_current_member(
        self,
        *,
        guild_id: SnowflakeType,
        nick: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/guild#modify-current-member"""
        ...
    async def modify_current_user_nick(
        self,
        *,
        guild_id: SnowflakeType,
        nick: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/guild#modify-current-user-nick"""
        ...
    async def add_guild_member_role(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        role_id: SnowflakeType,
        reason: Optional[str] = ...,
    ):
        """https://discord.com/developers/docs/resources/guild#add-guild-member-role"""
        ...
    async def remove_guild_member_role(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        role_id: SnowflakeType,
        reason: Optional[str] = ...,
    ):
        """https://discord.com/developers/docs/resources/guild#remove-guild-member-role"""
        ...
    async def remove_guild_member(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        reason: Optional[str] = ...,
    ):
        """https://discord.com/developers/docs/resources/guild#remove-guild-member"""
        ...
    async def get_guild_bans(
        self,
        *,
        guild_id: SnowflakeType,
        limit: Optional[int] = ...,
        before: Optional[SnowflakeType] = ...,
        after: Optional[SnowflakeType] = ...,
    ) -> List[Ban]:
        """https://discord.com/developers/docs/resources/guild#get-guild-bans"""
        ...
    async def get_guild_ban(
        self, *, guild_id: SnowflakeType, user_id: SnowflakeType
    ) -> Ban:
        """https://discord.com/developers/docs/resources/guild#get-guild-ban"""
        ...
    async def create_guild_ban(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        delete_message_days: Optional[int] = ...,
        delete_message_seconds: Optional[int] = ...,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#create-guild-ban"""
        ...
    async def remove_guild_ban(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#remove-guild-ban"""
        ...
    async def get_guild_roles(self, *, guild_id: SnowflakeType) -> List[Role]:
        """https://discord.com/developers/docs/resources/guild#get-guild-roles"""
        ...
    async def create_guild_role(
        self,
        *,
        guild_id: SnowflakeType,
        name: Optional[str] = ...,
        permissions: Optional[str] = ...,
        color: Optional[int] = ...,
        hoist: Optional[bool] = ...,
        icon: Optional[str] = ...,
        unicode_emoji: Optional[str] = ...,
        mentionable: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> Role:
        """https://discord.com/developers/docs/resources/guild#create-guild-role"""
        ...
    async def modify_guild_role_positions(
        self,
        *,
        guild_id: SnowflakeType,
        id: SnowflakeType,
        position: Optional[int] = ...,
        reason: Optional[str] = ...,
    ) -> List[Role]:
        """https://discord.com/developers/docs/resources/guild#modify-guild-role-positions"""
        ...
    async def modify_guild_role(
        self,
        *,
        guild_id: SnowflakeType,
        role_id: SnowflakeType,
        name: Optional[str] = ...,
        permissions: Optional[str] = ...,
        color: Optional[int] = ...,
        hoist: Optional[bool] = ...,
        icon: Optional[str] = ...,
        unicode_emoji: Optional[str] = ...,
        mentionable: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> Role:
        """https://discord.com/developers/docs/resources/guild#modify-guild-role"""
        ...
    async def modify_guild_MFA_level(
        self, *, guild_id: SnowflakeType, level: int, reason: Optional[str] = ...
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#modify-guild-mfa-level"""
        ...
    async def delete_guild_role(
        self,
        *,
        guild_id: SnowflakeType,
        role_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#delete-guild-role"""
        ...
    async def get_guild_prune_count(
        self, *, guild_id: SnowflakeType, days: int, include_roles: List[SnowflakeType]
    ) -> Dict[Literal["pruned"], int]:
        """https://discord.com/developers/docs/resources/guild#get-guild-prune-count"""
        ...
    async def begin_guild_prune(
        self,
        *,
        guild_id: SnowflakeType,
        days: Optional[int] = ...,
        compute_prune_count: Optional[bool] = ...,
        include_roles: Optional[List[SnowflakeType]] = ...,
        reason: Optional[str] = ...,
    ) -> Dict[Literal["pruned"], int]:
        """https://discord.com/developers/docs/resources/guild#begin-guild-prune"""
        ...
    async def get_guild_voice_regions(
        self, *, guild_id: SnowflakeType
    ) -> List[VoiceRegion]:
        """https://discord.com/developers/docs/resources/guild#get-guild-voice-regions"""
        ...
    async def get_guild_invites(self, *, guild_id: SnowflakeType) -> List[Invite]:
        """https://discord.com/developers/docs/resources/guild#get-guild-invites"""
        ...
    async def get_guild_integrations(
        self, *, guild_id: SnowflakeType
    ) -> List[Integration]:
        """https://discord.com/developers/docs/resources/guild#get-guild-integrations"""
        ...
    async def delete_guild_integration(
        self,
        *,
        guild_id: SnowflakeType,
        integration_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#delete-guild-integration"""
        ...
    async def get_guild_widget_settings(
        self, *, guild_id: SnowflakeType
    ) -> GuildWidgetSettings:
        """https://discord.com/developers/docs/resources/guild#get-guild-widget-settings"""
        ...
    async def modify_guild_widget(
        self,
        *,
        guild_id: SnowflakeType,
        enabled: Optional[bool] = ...,
        channel_id: Optional[SnowflakeType] = ...,
        reason: Optional[str] = ...,
    ) -> GuildWidget:
        """https://discord.com/developers/docs/resources/guild#modify-guild-widget"""
        ...
    async def get_guild_widget(self, *, guild_id: SnowflakeType) -> GuildWidget:
        """https://discord.com/developers/docs/resources/guild#get-guild-widget"""
        ...
    async def get_guild_vanity_url(self, *, guild_id: SnowflakeType) -> Invite:
        """https://discord.com/developers/docs/resources/guild#get-guild-vanity-url"""
        ...
    async def get_guild_widget_image(
        self,
        *,
        guild_id: SnowflakeType,
        style: Optional[
            Literal["shield", "banner1", "banner2", "banner3", "banner4"]
        ] = ...,
    ) -> str:
        """https://discord.com/developers/docs/resources/guild#get-guild-widget-image"""
        ...
    async def get_guild_welcome_screen(
        self, *, guild_id: SnowflakeType
    ) -> WelcomeScreen:
        """https://discord.com/developers/docs/resources/guild#get-guild-welcome-screen"""
        ...
    async def modify_guild_welcome_screen(
        self,
        *,
        guild_id: SnowflakeType,
        enabled: Optional[bool] = ...,
        welcome_channels: Optional[List[WelcomeScreenChannel]] = ...,
        description: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> WelcomeScreen:
        """https://discord.com/developers/docs/resources/guild#modify-guild-welcome-screen"""
        ...
    async def get_guild_onboarding(self, *, guild_id: SnowflakeType) -> GuildOnboarding:
        """https://discord.com/developers/docs/resources/guild#get-guild-onboarding"""
        ...
    async def modify_current_user_voice_state(
        self,
        *,
        guild_id: SnowflakeType,
        channel_id: Optional[SnowflakeType] = ...,
        suppress: Optional[bool] = ...,
        request_to_speak_timestamp: Optional[datetime.datetime] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#modify-current-user-voice-state"""
        ...
    async def modify_user_voice_state(
        self,
        *,
        guild_id: SnowflakeType,
        user_id: SnowflakeType,
        channel_id: SnowflakeType,
        suppress: Optional[bool] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/guild#modify-user-voice-state"""
        ...
    async def list_scheduled_events_for_guild(
        self, *, guild_id: SnowflakeType, with_user_count: Optional[bool] = ...
    ) -> List[GuildScheduledEvent]:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#list-scheduled-events-for-guild"""
        ...
    async def create_guild_schedule_event(
        self,
        *,
        guild_id: SnowflakeType,
        channel_id: Optional[Snowflake] = ...,
        entity_metadata: Optional[GuildScheduledEventEntityMetadata] = ...,
        name: str,
        privacy_level: GuildScheduledEventPrivacyLevel,
        scheduled_start_time: datetime.datetime,
        scheduled_end_time: Optional[datetime.datetime] = ...,
        description: Optional[str] = ...,
        entity_type: GuildScheduledEventEntityType,
        image: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#create-guild-scheduled-event"""
        ...
    async def get_guild_scheduled_event(
        self,
        *,
        guild_id: SnowflakeType,
        event_id: SnowflakeType,
        with_user_count: Optional[bool] = ...,
    ) -> GuildScheduledEvent:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#get-guild-scheduled-event"""
        ...
    async def modify_guild_scheduled_event(
        self,
        *,
        guild_id: SnowflakeType,
        event_id: SnowflakeType,
        channel_id: Optional[Snowflake] = ...,
        entity_metadata: Optional[GuildScheduledEventEntityMetadata] = ...,
        name: Optional[str] = ...,
        privacy_level: Optional[GuildScheduledEventPrivacyLevel] = ...,
        scheduled_start_time: Optional[datetime.datetime] = ...,
        scheduled_end_time: Optional[datetime.datetime] = ...,
        description: Optional[str] = ...,
        entity_type: Optional[GuildScheduledEventEntityType] = ...,
        status: Optional[GuildScheduledEventStatus] = ...,
        image: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#modify-guild-scheduled-event"""
        ...
    async def delete_guild_scheduled_event(
        self, *, guild_id: SnowflakeType, event_id: SnowflakeType
    ) -> None:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#delete-guild-scheduled-event"""
        ...
    async def get_guild_scheduled_event_users(
        self,
        *,
        guild_id: SnowflakeType,
        event_id: SnowflakeType,
        limit: Optional[int] = ...,
        with_member: Optional[bool] = ...,
        before: Optional[SnowflakeType] = ...,
        after: Optional[SnowflakeType] = ...,
    ) -> List[GuildScheduledEventUser]:
        """https://discord.com/developers/docs/resources/guild-scheduled-event#get-guild-scheduled-event-users"""
        ...
    async def get_guild_template(self, *, template_code: str) -> GuildTemplate:
        """https://discord.com/developers/docs/resources/guild-template#get-guild-template"""
        ...
    async def create_guild_from_guild_template(
        self, *, template_code: str, name: str, icon: Optional[str] = ...
    ) -> Guild:
        """https://discord.com/developers/docs/resources/guild-template#create-guild-from-template"""
        ...
    async def get_guild_templates(
        self, *, guild_id: SnowflakeType
    ) -> List[GuildTemplate]:
        """https://discord.com/developers/docs/resources/guild-template#get-guild-templates"""
        ...
    async def create_guild_template(
        self, *, guild_id: SnowflakeType, name: str, description: Optional[str] = ...
    ) -> GuildTemplate:
        """https://discord.com/developers/docs/resources/guild-template#create-guild-template"""
        ...
    async def sync_guild_template(
        self, *, guild_id: SnowflakeType, template_code: str
    ) -> GuildTemplate:
        """https://discord.com/developers/docs/resources/guild-template#sync-guild-template"""
        ...
    async def modify_guild_template(
        self,
        *,
        guild_id: SnowflakeType,
        template_code: str,
        name: Optional[str] = ...,
        description: Optional[str] = ...,
    ) -> GuildTemplate:
        """https://discord.com/developers/docs/resources/guild-template#modify-guild-template"""
        ...
    async def delete_guild_template(
        self, *, guild_id: SnowflakeType, template_code: str
    ) -> None:
        """https://discord.com/developers/docs/resources/guild-template#delete-guild-template"""
        ...
    async def get_invite(
        self,
        *,
        invite_code: str,
        with_counts: Optional[bool] = ...,
        with_expiration: Optional[bool] = ...,
        guild_scheduled_event_id: Optional[SnowflakeType] = ...,
    ) -> Invite:
        """https://discord.com/developers/docs/resources/invite#get-invite"""
        ...
    async def delete_invite(
        self, *, invite_code: str, reason: Optional[str] = ...
    ) -> Invite:
        """https://discord.com/developers/docs/resources/invite#delete-invite"""
        ...
    async def create_stage_instance(
        self,
        *,
        channel_id: SnowflakeType,
        topic: str,
        privacy_level: Optional[StagePrivacyLevel] = ...,
        send_start_notification: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> StageInstance:
        """https://discord.com/developers/docs/resources/stage-instance#create-stage-instance"""
        ...
    async def get_stage_instance(
        self, *, channel_id: SnowflakeType
    ) -> Optional[StageInstance]:
        """https://discord.com/developers/docs/resources/stage-instance#get-stage-instance"""
        ...
    async def modify_stage_instance(
        self,
        *,
        channel_id: SnowflakeType,
        topic: Optional[str] = ...,
        privacy_level: Optional[StagePrivacyLevel] = ...,
        reason: Optional[str] = ...,
    ) -> StageInstance:
        """https://discord.com/developers/docs/resources/stage-instance#modify-stage-instance"""
        ...
    async def delete_stage_instance(
        self, *, channel_id: SnowflakeType, reason: Optional[str] = ...
    ) -> None:
        """https://discord.com/developers/docs/resources/stage-instance#delete-stage-instance"""
        ...
    async def get_sticker(self, *, sticker_id: SnowflakeType) -> Sticker:
        """https://discord.com/developers/docs/resources/sticker#get-sticker"""
        ...
    async def list_nitro_sticker_packs(self) -> List[StickerPack]:
        """https://discord.com/developers/docs/resources/sticker#list-nitro-sticker-packs"""
        ...
    async def list_guild_stickers(self, *, guild_id: SnowflakeType) -> List[Sticker]:
        """https://discord.com/developers/docs/resources/sticker#list-guild-stickers"""
        ...
    async def get_guild_sticker(
        self, *, guild_id: SnowflakeType, sticker_id: SnowflakeType
    ) -> Sticker:
        """https://discord.com/developers/docs/resources/sticker#get-guild-sticker"""
        ...
    # async def create_guild_sticker(self,
    #                                *,
    #                                guild_id: SnowflakeType,
    #                                name: str,
    #                                description: str,
    #                                tags: str,
    #                                file: File,
    #                                reason: Optional[str] = ...) -> Sticker:
    #     """https://discord.com/developers/docs/resources/sticker#create-guild-sticker"""
    #     ...

    async def modify_guild_sticker(
        self,
        *,
        guild_id: SnowflakeType,
        sticker_id: SnowflakeType,
        name: Optional[str] = ...,
        description: Optional[str] = ...,
        tags: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> Sticker:
        """https://discord.com/developers/docs/resources/sticker#modify-guild-sticker"""
        ...
    async def delete_guild_sticker(
        self,
        *,
        guild_id: SnowflakeType,
        sticker_id: SnowflakeType,
        reason: Optional[str] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/sticker#delete-guild-sticker"""
        ...
    async def get_current_user(self) -> User:
        """https://discord.com/developers/docs/resources/user#get-current-user"""
        ...
    async def get_user(self, *, user_id: SnowflakeType) -> User:
        """https://discord.com/developers/docs/resources/user#get-user"""
        ...
    async def modify_current_user(
        self, *, username: Optional[str] = ..., avatar: Optional[str] = ...
    ) -> User:
        """https://discord.com/developers/docs/resources/user#modify-current-user"""
        ...
    async def get_current_user_guilds(
        self,
        *,
        before: Optional[SnowflakeType] = ...,
        after: Optional[SnowflakeType] = ...,
        limit: Optional[int] = ...,
    ) -> List[CurrentUserGuild]:
        """https://discord.com/developers/docs/resources/user#get-current-user-guilds"""
        ...
    async def get_current_user_guild_member(
        self, *, guild_id: SnowflakeType
    ) -> GuildMember:
        """https://discord.com/developers/docs/resources/user#get-current-user-guild-member"""
        ...
    async def leave_guild(self, *, guild_id: SnowflakeType) -> None:
        """https://discord.com/developers/docs/resources/user#leave-guild"""
        ...
    async def create_DM(self, *, recipient_id: SnowflakeType) -> Channel:
        """https://discord.com/developers/docs/resources/user#create-dm"""
        ...
    async def create_group_DM(
        self, *, access_tokens: List[str], nicks: Dict[SnowflakeType, str]
    ) -> Channel:
        """https://discord.com/developers/docs/resources/user#create-group-dm"""
        ...
    async def get_user_connections(self) -> List[Connection]:
        """https://discord.com/developers/docs/resources/user#get-user-connections"""
        ...
    async def get_user_application_role_connection(
        self, *, application_id: SnowflakeType
    ) -> ApplicationRoleConnection:
        """https://discord.com/developers/docs/resources/user#get-user-application-connections"""
        ...
    async def update_user_application_role_connection(
        self,
        *,
        application_id: SnowflakeType,
        platform_name: Optional[str] = ...,
        platform_username: Optional[str] = ...,
        metadata: Optional[ApplicationRoleConnectionMetadata] = ...,
    ) -> ApplicationRoleConnection:
        """https://discord.com/developers/docs/resources/user#modify-current-user"""
        ...
    async def list_voice_regions(self) -> List[VoiceRegion]:
        """https://discord.com/developers/docs/resources/voice#list-voice-regions"""
        ...
    async def create_webhook(
        self,
        *,
        channel_id: SnowflakeType,
        name: str,
        avatar: Optional[str] = ...,
        reason: Optional[str] = ...,
    ) -> Webhook:
        """https://discord.com/developers/docs/resources/webhook#create-webhook"""
        ...
    async def get_channel_webhooks(self, *, channel_id: SnowflakeType) -> List[Webhook]:
        """https://discord.com/developers/docs/resources/webhook#get-channel-webhooks"""
        ...
    async def get_guild_webhooks(self, *, guild_id: SnowflakeType) -> List[Webhook]:
        """https://discord.com/developers/docs/resources/webhook#get-guild-webhooks"""
        ...
    async def get_webhook(self, *, webhook_id: SnowflakeType) -> Webhook:
        """https://discord.com/developers/docs/resources/webhook#get-webhook"""
        ...
    async def get_webhook_with_token(
        self, *, webhook_id: SnowflakeType, token: str
    ) -> Webhook:
        """https://discord.com/developers/docs/resources/webhook#get-webhook-with-token"""
        ...
    async def modify_webhook(
        self,
        *,
        webhook_id: SnowflakeType,
        name: Optional[str] = ...,
        avatar: Optional[str] = ...,
        channel_id: Optional[SnowflakeType] = ...,
        reason: Optional[str] = ...,
    ) -> Webhook:
        """https://discord.com/developers/docs/resources/webhook#modify-webhook"""
        ...
    async def modify_webhook_with_token(
        self,
        *,
        webhook_id: SnowflakeType,
        token: str,
        name: Optional[str] = ...,
        avatar: Optional[str] = ...,
    ) -> Webhook:
        """https://discord.com/developers/docs/resources/webhook#modify-webhook-with-token"""
        ...
    async def delete_webhook(
        self, *, webhook_id: SnowflakeType, reason: Optional[str] = ...
    ) -> None:
        """https://discord.com/developers/docs/resources/webhook#delete-webhook"""
        ...
    async def delete_webhook_with_token(
        self, *, webhook_id: SnowflakeType, token: str
    ) -> None:
        """https://discord.com/developers/docs/resources/webhook#delete-webhook-with-token"""
        ...
    # async def execute_webhook(self,
    #                           *,
    #
    #                           webhook_id: SnowflakeType,
    #                           token: str,
    #                           **data) -> None:
    #     """https://discord.com/developers/docs/resources/webhook#execute-webhook"""
    #     ...

    async def execute_slack_compatible_webhook(
        self,
        *,
        webhook_id: SnowflakeType,
        token: str,
        thread_id: Optional[SnowflakeType] = ...,
        wait: Optional[bool] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/webhook#execute-slackcompatible-webhook"""
        ...
    async def execute_github_compatible_webhook(
        self,
        *,
        webhook_id: SnowflakeType,
        token: str,
        thread_id: Optional[SnowflakeType] = ...,
        wait: Optional[bool] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/webhook#execute-githubcompatible-webhook"""
        ...
    async def get_webhook_message(
        self,
        *,
        webhook_id: SnowflakeType,
        token: str,
        message_id: SnowflakeType,
        thread_id: Optional[SnowflakeType] = ...,
    ) -> MessageGet:
        """https://discord.com/developers/docs/resources/webhook#get-webhook-message"""
        ...
    # async def edit_webhook_message(self) -> Message:
    #     """https://discord.com/developers/docs/resources/webhook#edit-webhook-message"""
    #     ...

    async def delete_webhook_message(
        self,
        *,
        webhook_id: SnowflakeType,
        token: str,
        message_id: SnowflakeType,
        thread_id: Optional[SnowflakeType] = ...,
    ) -> None:
        """https://discord.com/developers/docs/resources/webhook#delete-webhook-message"""
        ...
    async def get_gateway(self) -> Gateway:
        """https://discord.com/developers/docs/topics/gateway#get-gateway"""
        ...
    async def get_gateway_bot(self) -> GatewayBot:
        """https://discord.com/developers/docs/topics/gateway#get-gateway-bot"""
        ...
    async def get_current_bot_application_information(self) -> Application:
        """https://discord.com/developers/docs/resources/user#get-current-application-information"""
        ...
    async def get_current_authorization_information(self) -> AuthorizationResponse:
        """https://discord.com/developers/docs/resources/user#get-current-authorization-information"""
        ...
