from typing import List, Tuple, Optional

from pydantic import Extra, Field, BaseModel


class Intents(BaseModel):
    guilds: bool = True
    guild_members: bool = True
    guild_moderation: bool = True
    guild_emojis_and_stickers: bool = True
    guild_integrations: bool = False
    guild_webhooks: bool = False
    guild_invites: bool = True
    guild_voice_states: bool = False
    guild_presences: bool = True
    guild_messages: bool = True
    guild_message_reactions: bool = True
    guild_message_typing: bool = True
    direct_messages: bool = True
    direct_message_reactions: bool = True
    direct_message_typing: bool = True
    message_content: bool = True
    guild_scheduled_events: bool = False
    auto_moderation_configuration: bool = False
    auto_moderation_execution: bool = False

    def to_int(self):
        return (
            self.guilds << 0
            | self.guild_members << 1
            | self.guild_moderation << 2
            | self.guild_emojis_and_stickers << 3
            | self.guild_integrations << 4
            | self.guild_webhooks << 5
            | self.guild_invites << 6
            | self.guild_voice_states << 7
            | self.guild_presences << 8
            | self.guild_messages << 9
            | self.guild_message_reactions << 10
            | self.guild_message_typing << 11
            | self.direct_messages << 12
            | self.direct_message_reactions << 13
            | self.direct_message_typing << 14
            | self.message_content << 15
            | self.guild_scheduled_events << 16
            | self.auto_moderation_configuration << 20
            | self.auto_moderation_execution << 21
        )


class BotInfo(BaseModel):
    token: str
    shard: Optional[Tuple[int, int]] = None
    intent: Intents = Field(default_factory=Intents)


class Config(BaseModel, extra=Extra.ignore):
    discord_bots: List[BotInfo] = Field(default_factory=list)
    discord_compress: bool = False
    discord_api_version: int = 10
    discord_api_timeout: float = 30.0
    discord_handle_self_message: bool = False
    discord_proxy: Optional[str] = None
