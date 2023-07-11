import re
import datetime
from dataclasses import dataclass
from typing import Type, Union, Iterable, Optional, TypedDict, overload

from nonebot.typing import overrides
from nonebot.utils import escape_tag

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import escape
from .api import (
    File,
    Embed,
    Button,
    ActionRow,
    Component,
    Snowflake,
    MessageGet,
    SelectMenu,
    SnowflakeType,
    AttachmentSend,
    TimeStampStyle,
    DirectComponent,
    MessageReference,
)


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @staticmethod
    def attachment(
        file: Union[str, File, AttachmentSend],
        description: Optional[str] = None,
        content: Optional[bytes] = None,
    ) -> "AttachmentSegment":
        if isinstance(file, str):
            _filename = file
            _description = description
            _content = content
        elif isinstance(file, File):
            _filename = file.filename
            _description = description
            _content = file.content
        elif isinstance(file, AttachmentSend):
            _filename = file.filename
            _description = file.description
            _content = content
        else:
            raise TypeError("file must be str, File or AttachmentSend")
        if _content is None:
            return AttachmentSegment(
                data={
                    "attachment": AttachmentSend(
                        filename=_filename, description=_description
                    ),
                    "file": None,
                }
            )
        else:
            return AttachmentSegment(
                data={
                    "attachment": AttachmentSend(
                        filename=_filename, description=_description
                    ),
                    "file": File(filename=_filename, content=_content),
                }
            )

    @staticmethod
    def sticker(sticker_id: SnowflakeType) -> "StickerSegment":
        return StickerSegment(data={"id": Snowflake(sticker_id)})

    @staticmethod
    def embed(embed: Embed) -> "EmbedSegment":
        return EmbedSegment(data={"embed": embed})

    @staticmethod
    def component(component: Component):
        if isinstance(component, (Button, SelectMenu)):
            component = ActionRow(components=[component])
        return ComponentSegment(data={"component": component})

    @staticmethod
    def custom_emoji(
        name: str, emoji_id: str, animated: Optional[bool] = None
    ) -> "CustomEmojiSegment":
        return CustomEmojiSegment(
            data={"name": name, "id": emoji_id, "animated": animated}
        )

    @staticmethod
    def mention_user(user_id: SnowflakeType) -> "MentionUserSegment":
        return MentionUserSegment(data={"user_id": Snowflake(user_id)})

    @staticmethod
    def mention_role(role_id: SnowflakeType) -> "MentionRoleSegment":
        return MentionRoleSegment(data={"role_id": Snowflake(role_id)})

    @staticmethod
    def mention_channel(channel_id: SnowflakeType) -> "MentionChannelSegment":
        return MentionChannelSegment(data={"channel_id": Snowflake(channel_id)})

    @staticmethod
    def mention_everyone() -> "MentionEveryoneSegment":
        return MentionEveryoneSegment()

    @staticmethod
    def text(content: str) -> "TextSegment":
        return TextSegment(data={"text": escape(content)})

    @staticmethod
    def timestamp(
        timestamp: Union[int, datetime.datetime], style: Optional[TimeStampStyle] = None
    ) -> "TimestampSegment":
        if isinstance(timestamp, datetime.datetime):
            timestamp = int(timestamp.timestamp())
        return TimestampSegment(data={"timestamp": timestamp, "style": style})

    @staticmethod
    @overload
    def reference(reference: MessageReference) -> "ReferenceSegment":
        ...

    @staticmethod
    @overload
    def reference(
        reference: SnowflakeType,
        channel_id: Optional[SnowflakeType] = None,
        guild_id: Optional[SnowflakeType] = None,
        fail_if_not_exists: Optional[bool] = None,
    ) -> "ReferenceSegment":
        ...

    @staticmethod
    def reference(
        reference: Union[SnowflakeType, MessageReference],
        channel_id: Optional[SnowflakeType] = None,
        guild_id: Optional[SnowflakeType] = None,
        fail_if_not_exists: Optional[bool] = None,
    ):
        if isinstance(reference, MessageReference):
            _reference = reference
        else:
            _reference = MessageReference.parse_obj(
                {
                    "message_id": reference,
                    "channel_id": channel_id,
                    "guild_id": guild_id,
                    "fail_if_not_exists": fail_if_not_exists,
                }
            )

        return ReferenceSegment(data={"reference": _reference})

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == "text"


@dataclass
class StickerSegment(MessageSegment):
    type: str = "sticker"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<Sticker:{self.data['id']}>"


ComponentData = TypedDict("ComponentData", {"component": DirectComponent})


@dataclass
class ComponentSegment(MessageSegment):
    type: str = "component"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<Component:{self.data['component'].type}>"


CustomEmojiData = TypedDict(
    "CustomEmojiData", {"name": str, "id": str, "animated": Optional[bool]}
)


@dataclass
class CustomEmojiSegment(MessageSegment):
    type: str = "custom_emoji"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        if self.data.get("animated"):
            return f"<a:{self.data['name']}:{self.data['id']}>"
        else:
            return f"<:{self.data['name']}:{self.data['id']}>"


MentionUserData = TypedDict("MentionUserData", {"user_id": Snowflake})


@dataclass
class MentionUserSegment(MessageSegment):
    type: str = "mention_user"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<@{self.data['user_id']}>"


MentionChannelData = TypedDict("MentionChannelData", {"channel_id": Snowflake})


@dataclass
class MentionChannelSegment(MessageSegment):
    type: str = "mention_channel"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<#{self.data['channel_id']}>"


MentionRoleData = TypedDict("MentionRoleData", {"role_id": Snowflake})


@dataclass
class MentionRoleSegment(MessageSegment):
    type: str = "mention_role"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<@&{self.data['role_id']}>"


@dataclass
class MentionEveryoneSegment(MessageSegment):
    type: str = "mention_everyone"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return "@everyone"


TimestampData = TypedDict(
    "TimestampData", {"timestamp": int, "style": Optional[TimeStampStyle]}
)


@dataclass
class TimestampSegment(MessageSegment):
    type: str = "timestamp"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        style = self.data.get("style")
        return (
            f"<t:{self.data['timestamp']}"
            + (
                f":{style.value if isinstance(style, TimeStampStyle) else style}"
                if style
                else ""
            )
            + ">"
        )


TextData = TypedDict("TextData", {"text": str})


@dataclass
class TextSegment(MessageSegment):
    type: str = "text"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return escape_tag(self.data["text"])


EmbedData = TypedDict("EmbedData", {"embed": Embed})


@dataclass
class EmbedSegment(MessageSegment):
    type: str = "embed"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<Embed:{self.data['embed'].type}>"


AttachmentData = TypedDict(
    "AttachmentData", {"attachment": AttachmentSend, "file": Optional[File]}
)


@dataclass
class AttachmentSegment(MessageSegment):
    type: str = "attachment"

    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<Attachment:{self.data['attachment'].filename}>"


ReferenceData = TypedDict("ReferenceData", {"reference": MessageReference})


@dataclass
class ReferenceSegment(MessageSegment):
    type: str = "reference"

    @overrides(MessageSegment)
    def __str__(self):
        return f"<Reference:{self.data['reference'].message_id}>"


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessage)
    def __radd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        text_begin = 0
        for embed in re.finditer(
            r"<(?P<type>(@!|@&|@|#|/|:|a:|t:))?(?P<param>.+?)>",
            msg,
        ):
            if content := msg[text_begin : embed.pos + embed.start()]:
                yield TextSegment(data={"text": escape(content)})
            text_begin = embed.pos + embed.end()
            if embed.group("type") in ("@!", "@"):
                yield MentionUserSegment(
                    data={"user_id": Snowflake(embed.group("param"))}
                )
            elif embed.group("type") == "@&":
                yield MentionRoleSegment(
                    data={"role_id": Snowflake(embed.group("param"))}
                )
            elif embed.group("type") == "#":
                yield MentionChannelSegment(
                    data={"channel_id": Snowflake(embed.group("param"))}
                )
            elif embed.group("type") == "/":
                # TODO: slash command
                pass
            elif embed.group("type") in (":", "a:"):
                if len(cut := embed.group("param").split(":")) == 2:
                    yield CustomEmojiSegment(
                        data={
                            "name": cut[0],
                            "id": cut[1],
                            "animated": embed.group("type") == "a:",
                        }
                    )
                else:
                    yield TextSegment(data={"text": escape(embed.group())})
            else:
                if (
                    len(cut := embed.group("param").split(":")) == 2
                    and cut[0].isdigit()
                ):
                    yield TimestampSegment(
                        data={"timestamp": int(cut[0]), "style": TimeStampStyle(cut[1])}
                    )
                elif embed.group().isdigit():
                    yield TimestampSegment(
                        data={"timestamp": int(embed.group()), "style": None}
                    )
                else:
                    yield TextSegment(data={"text": escape(embed.group())})
        if content := msg[text_begin:]:
            yield TextSegment(data={"text": escape(content)})

    @classmethod
    def from_guild_message(cls, message: MessageGet) -> "Message":
        msg = Message()
        if message.mention_everyone:
            msg.append(MessageSegment.mention_everyone())
        if message.content:
            msg.extend(Message(message.content))
        if message.attachments:
            msg.extend(
                AttachmentSegment(
                    data={
                        "attachment": AttachmentSend(
                            filename=attachment.filename,
                            description=attachment.description or None,
                        ),
                        "file": None,
                    }
                )
                for attachment in message.attachments
            )
        if message.embeds:
            msg.extend(EmbedSegment(data={"embed": embed}) for embed in message.embeds)
        if message.components:
            msg.extend(
                ComponentSegment(data={"component": component})
                for component in message.components
            )
        return msg

    def extract_content(self) -> str:
        return "".join(
            str(seg)
            for seg in self
            if seg.type
            in (
                "text",
                "custom_emoji",
                "mention_user",
                "mention_role",
                "mention_everyone",
                "mention_channel",
                "timestamp",
            )
        )
