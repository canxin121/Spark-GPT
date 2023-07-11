from typing import TYPE_CHECKING, Any, Union, Optional

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot

from .utils import log
from .config import BotInfo
from .event import Event, MessageEvent
from .message import Message, MessageSegment
from .api import User, ApiClient, MessageGet, AllowedMention, MessageReference

if TYPE_CHECKING:
    from .adapter import Adapter


async def _check_reply(bot: "Bot", event: MessageEvent) -> None:
    if not event.message_reference or not event.message_reference.message_id:
        return
    try:
        event.reply = await bot.get_channel_message(
            channel_id=event.channel_id, message_id=event.message_reference.message_id
        )
        if event.reply.author.id == bot.self_info.id:
            event.to_me = True
    except Exception as e:
        log("WARNING", f"Error when getting message reply info: {repr(e)}", e)


def _check_at_me(bot: "Bot", event: MessageEvent) -> None:
    if event.mentions is not None and bot.self_info.id in [
        user.id for user in event.mentions
    ]:
        event.to_me = True

    def _is_at_me_seg(segment: MessageSegment) -> bool:
        return (
            segment.type == "mention_user"
            and segment.data.get("user_id") == bot.self_info.id
        )

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    deleted = False
    if _is_at_me_seg(message[0]):
        message.pop(0)
        deleted = True
        if message and message[0].type == "text":
            message[0].data["text"] = message[0].data["text"].lstrip("\xa0").lstrip()
            if not message[0].data["text"]:
                del message[0]

    if not deleted:
        # check the last segment
        i = -1
        last_msg_seg = message[i]
        if (
            last_msg_seg.type == "text"
            and not last_msg_seg.data["text"].strip()
            and len(message) >= 2
        ):
            i -= 1
            last_msg_seg = message[i]

        if _is_at_me_seg(last_msg_seg):
            deleted = True
            del message[i:]

    if not message:
        message.append(MessageSegment.text(""))


class Bot(BaseBot, ApiClient):
    """
    Discord 协议 Bot 适配。
    """

    @overrides(BaseBot)
    def __init__(self, adapter: "Adapter", self_id: str, bot_info: BotInfo):
        super().__init__(adapter, self_id)
        self.adapter = adapter
        self.bot_info: BotInfo = bot_info
        self._session_id: Optional[str] = None
        self._self_info: Optional[User] = None
        self._sequence: Optional[int] = None

    @overrides(BaseBot)
    def __repr__(self) -> str:
        return f"Bot(type={self.type!r}, self_id={self.self_id!r})"

    @property
    def ready(self) -> bool:
        return self._session_id is not None

    @property
    def session_id(self) -> str:
        if self._session_id is None:
            raise RuntimeError(f"Bot {self.self_id} is not connected!")
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: str) -> None:
        self._session_id = session_id

    @property
    def self_info(self) -> User:
        if self._self_info is None:
            raise RuntimeError(f"Bot {self.bot_info} is not connected!")
        return self._self_info

    @self_info.setter
    def self_info(self, self_info: User) -> None:
        self._self_info = self_info

    @property
    def has_sequence(self) -> bool:
        return self._sequence is not None

    @property
    def sequence(self) -> int:
        if self._sequence is None:
            raise RuntimeError(f"Bot {self.self_id} is not connected!")
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: int) -> None:
        self._sequence = sequence

    def clear(self) -> None:
        self._session_id = None
        self._sequence = None

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, MessageEvent):
            await _check_reply(self, event)
            _check_at_me(self, event)
        await handle_event(self, event)

    @overrides(BaseBot)
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        mention_sender: bool = False,
        reply_message: bool = False,
        tts: bool = False,
        nonce: Union[int, str, None] = None,
        allowed_mentions: Optional[AllowedMention] = None,
        **params: Any,
    ) -> MessageGet:
        """send message.

        Args:
            event: Event Object
            message: message to send
            mention_sender: whether @ event subject
            reply_message: whether reply event message
            tts: whether send as a TTS message
            nonce: can be used to verify a message was sent
            allowed_mentions: allowed mentions for the message
            **params: other params

        Returns:
            message model
        """
        if not isinstance(event, MessageEvent) or not event.channel_id or not event.id:
            raise RuntimeError("Event cannot be replied to!")
        message = MessageSegment.text(message) if isinstance(message, str) else message
        message = message if isinstance(message, Message) else Message(message)
        if mention_sender:
            message.insert(0, MessageSegment.mention_user(event.user_id))
        if reply_message:
            message += MessageSegment.reference(MessageReference(message_id=event.id))

        content = message.extract_content() or None
        if embeds := (message["embed"] or None):
            embeds = [embed.data["embed"] for embed in embeds]
        if reference := (message["reference"] or None):
            reference = reference[-1].data["reference"]
        if components := (message["component"] or None):
            components = [component.data["component"] for component in components]
        if sticker_ids := (message["sticker"] or None):
            sticker_ids = [sticker.data["id"] for sticker in sticker_ids]

        attachments = None
        files = None
        if attachments_segment := (message["attachment"] or None):
            attachments = [
                attachment.data["attachment"] for attachment in attachments_segment
            ]
            files = [
                attachment.data["file"]
                for attachment in attachments_segment
                if attachment.data["file"] is not None
            ]

        return await self.create_message(
            channel_id=event.channel_id,
            content=content,
            nonce=nonce,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=reference,  # type: ignore
            components=components,
            sticker_ids=sticker_ids,
            files=files,
            attachments=attachments,
            **params,
        )
