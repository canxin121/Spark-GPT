from enum import Enum, IntEnum, IntFlag


class StrEnum(str, Enum):
    """String enum."""


class ActivityAssetImage(StrEnum):
    """Activity Asset Image

    see https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-asset-image
    """

    ApplicationAsset = "Application Asset"
    """{application_asset_id} see https://discord.com/developers/docs/reference#image-formatting"""
    MediaProxyImage = "Media Proxy Image"
    """mp:{image_id}"""


class ActivityFlags(IntFlag):
    """Activity Flags

    see https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-flags
    """

    INSTANCE = 1 << 0
    JOIN = 1 << 1
    SPECTATE = 1 << 2
    JOIN_REQUEST = 1 << 3
    SYNC = 1 << 4
    PLAY = 1 << 5
    PARTY_PRIVACY_FRIENDS = 1 << 6
    PARTY_PRIVACY_VOICE_CHANNEL = 1 << 7
    EMBEDDED = 1 << 8


class ActivityType(IntEnum):
    """Activity Type

    see https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-types
    """

    Game = 0
    """Playing {name}"""
    Streaming = 1
    """Streaming {details}"""
    Listening = 2
    """Listening to {name}"""
    Watching = 3
    """Watching {name}"""
    Custom = 4
    """{emoji} {name}"""
    Competing = 5
    """	Competing in {name}"""


class ApplicationCommandOptionType(IntEnum):
    """Application Command Option Type

    see https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type
    """

    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    """Any integer between -2^53 and 2^53"""
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    """Includes all channel types + categories"""
    ROLE = 8
    MENTIONABLE = 9
    """Includes users and roles"""
    NUMBER = 10
    """Any double between -2^53 and 2^53"""
    ATTACHMENT = 11
    """attachment object"""


class ApplicationCommandPermissionsType(IntEnum):
    """Application command permissions type.

    see https://discord.com/developers/docs/interactions/application-commands#application-command-permissions-object-application-command-permission-type
    """

    ROLE = 1
    USER = 2
    CHANNEL = 3


class ApplicationCommandType(IntEnum):
    """Application Command Type

    see https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-types
    """

    CHAT_INPUT = 1
    """Slash commands; a text-based command that shows up when a user types /"""
    USER = 2
    """A UI-based command that shows up when you right click or tap on a user"""
    MESSAGE = 3
    """A UI-based command that shows up when you right click or tap on a message"""


class ApplicationFlag(IntFlag):
    """Application flags.

    see https://discord.com/developers/docs/resources/application#application-object-application-flags
    """

    APPLICATION_AUTO_MODERATION_RULE_CREATE_BADGE = 1 << 6
    """Indicates if an app uses the Auto Moderation API"""
    GATEWAY_PRESENCE = 1 << 12
    """Intent required for bots in 100 or more servers to receive presence_update events"""
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    """Intent required for bots in under 100 servers to receive presence_update events, 
    found on the Bot page in your app's settings"""
    GATEWAY_GUILD_MEMBERS = 1 << 14
    """Intent required for bots in 100 or more servers to receive member-related events like guild_member_add. 
    See the list of member-related events under GUILD_MEMBERS"""
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    """Intent required for bots in under 100 servers to receive member-related events 
    like guild_member_add, found on the Bot page in your app's settings. 
    See the list of member-related events under GUILD_MEMBERS"""
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    """Indicates unusual growth of an app that prevents verification"""
    EMBEDDED = 1 << 17
    """Indicates if an app is embedded within the Discord client (currently unavailable publicly)"""
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    """Intent required for bots in 100 or more servers to receive message content"""
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    """Intent required for bots in under 100 servers to receive message content, 
    found on the Bot page in your app's settings"""
    APPLICATION_COMMAND_BADGE = 1 << 23
    """Indicates if an app has registered global application commands"""


class ApplicationRoleConnectionMetadataType(IntEnum):
    """Application role connection metadata type.

    see https://discord.com/developers/docs/resources/application-role-connection-metadata#application-role-connection-metadata-object-application-role-connection-metadata-type
    """

    INTEGER_LESS_THAN_OR_EQUAL = 1
    """the metadata value (integer) is less than or equal to the guild's configured value (integer)"""
    INTEGER_GREATER_THAN_OR_EQUAL = 2
    """the metadata value (integer) is greater than or equal to the guild's configured value (integer)"""
    INTEGER_EQUAL = 3
    """the metadata value (integer) is equal to the guild's configured value (integer)"""
    INTEGER_NOT_EQUAL = 4
    """	the metadata value (integer) is not equal to the guild's configured value (integer)"""
    DATETIME_LESS_THAN_OR_EQUAL = 5
    """	the metadata value (ISO8601 string) is less than or equal to the guild's configured value (integer; days before current date)"""
    DATETIME_GREATER_THAN_OR_EQUAL = 6
    """the metadata value (ISO8601 string) is greater than or equal to the guild's configured value (integer; days before current date)"""
    BOOLEAN_EQUAL = 7
    """the metadata value (integer) is equal to the guild's configured value (integer; 1)"""
    BOOLEAN_NOT_EQUAL = 8
    """the metadata value (integer) is not equal to the guild's configured value (integer; 1)"""


class AllowedMentionType(StrEnum):
    """Allowed mentions types.

    see https://discord.com/developers/docs/resources/channel#allowed-mentions-object-allowed-mention-types
    """

    RoleMentions = "roles"
    """Controls role mentions"""
    UserMentions = "users"
    """Controls user mentions"""
    EveryoneMentions = "everyone"
    """Controls @everyone and @here mentions"""


class AuditLogEventType(IntEnum):
    """Audit Log Event Type

    see https://discord.com/developers/docs/resources/audit-log#audit-log-entry-object-audit-log-events
    """

    GUILD_UPDATE = 1
    CHANNEL_CREATE = 10
    CHANNEL_UPDATE = 11
    CHANNEL_DELETE = 12
    CHANNEL_OVERWRITE_CREATE = 13
    CHANNEL_OVERWRITE_UPDATE = 14
    CHANNEL_OVERWRITE_DELETE = 15
    MEMBER_KICK = 20
    MEMBER_PRUNE = 21
    MEMBER_BAN_ADD = 22
    MEMBER_BAN_REMOVE = 23
    MEMBER_UPDATE = 24
    MEMBER_ROLE_UPDATE = 25
    MEMBER_MOVE = 26
    MEMBER_DISCONNECT = 27
    BOT_ADD = 28
    ROLE_CREATE = 30
    ROLE_UPDATE = 31
    ROLE_DELETE = 32
    INVITE_CREATE = 40
    INVITE_UPDATE = 41
    INVITE_DELETE = 42
    WEBHOOK_CREATE = 50
    WEBHOOK_UPDATE = 51
    WEBHOOK_DELETE = 52
    EMOJI_CREATE = 60
    EMOJI_UPDATE = 61
    EMOJI_DELETE = 62
    MESSAGE_DELETE = 72
    MESSAGE_BULK_DELETE = 73
    MESSAGE_PIN = 74
    MESSAGE_UNPIN = 75
    INTEGRATION_CREATE = 80
    INTEGRATION_UPDATE = 81
    INTEGRATION_DELETE = 82
    STAGE_INSTANCE_CREATE = 83
    STAGE_INSTANCE_UPDATE = 84
    STAGE_INSTANCE_DELETE = 85
    STICKER_CREATE = 90
    STICKER_UPDATE = 91
    STICKER_DELETE = 92
    GUILD_SCHEDULED_EVENT_CREATE = 100
    GUILD_SCHEDULED_EVENT_UPDATE = 101
    GUILD_SCHEDULED_EVENT_DELETE = 102
    THREAD_CREATE = 110
    THREAD_UPDATE = 111
    THREAD_DELETE = 112
    APPLICATION_COMMAND_PERMISSION_UPDATE = 121
    AUTO_MODERATION_RULE_CREATE = 140
    AUTO_MODERATION_RULE_UPDATE = 141
    AUTO_MODERATION_RULE_DELETE = 142
    AUTO_MODERATION_BLOCK_MESSAGE = 143
    AUTO_MODERATION_FLAG_TO_CHANNEL = 144
    AUTO_MODERATION_USER_COMMUNICATION_DISABLED = 145


class AutoModerationActionType(IntEnum):
    """Auto moderation action type.

    see https://discord.com/developers/docs/resources/auto-moderation#auto-moderation-action-object-action-types
    """

    BLOCK_MESSAGE = 1
    """blocks a member's message and prevents it from being posted. 
    A custom explanation can be specified and shown to members whenever their message is blocked."""
    SEND_ALERT_MESSAGE = 2
    """logs user content to a specified channel"""
    TIMEOUT = 3
    """timeout user for a specified duration.
    A TIMEOUT action can only be set up for KEYWORD and MENTION_SPAM rules. 
    The MODERATE_MEMBERS permission is required to use the TIMEOUT action type."""


class AutoModerationRuleEventType(IntEnum):
    """Auto moderation rule event type.

    see https://discord.com/developers/docs/resources/auto-moderation#auto-moderation-rule-object-event-types
    """

    MESSAGE_SEND = 1
    """when a member sends or edits a message in the guild"""


class ButtonStyle(IntEnum):
    """Button styles.

    see https://discord.com/developers/docs/interactions/message-components#button-object-button-styles
    """

    Primary = 1
    """color: blurple, required field: custom_id"""
    Secondary = 2
    """color: grey, required field: custom_id"""
    Success = 3
    """color: green, required field: custom_id"""
    Danger = 4
    """color: red, required field: custom_id"""
    Link = 5
    """color: grey, navigates to a URL, required field: url"""


class ChannelFlags(IntFlag):
    """Channel flags.

    see https://discord.com/developers/docs/resources/channel#channel-object-channel-flags
    """

    PINNED = 1 << 1
    """this thread is pinned to the top of its parent GUILD_FORUM channel"""
    REQUIRE_TAG = 1 << 4
    """whether a tag is required to be specified when creating a thread in a GUILD_FORUM channel. 
    Tags are specified in the applied_tags field."""


class ChannelType(IntEnum):
    """Channel type.

    see https://discord.com/developers/docs/resources/channel#channel-object-channel-types
    """

    GUILD_TEXT = 0
    """a text channel within a server"""
    DM = 1
    """a direct message between users"""
    GUILD_VOICE = 2
    """a voice channel within a server"""
    GROUP_DM = 3
    """a direct message between multiple users"""
    GUILD_CATEGORY = 4
    """an organizational category that contains up to 50 channels"""
    GUILD_ANNOUNCEMENT = 5
    """a channel that users can follow and crosspost into their own server (formerly news channels)"""
    ANNOUNCEMENT_THREAD = 10
    """a temporary sub-channel within a GUILD_ANNOUNCEMENT channel"""
    PUBLIC_THREAD = 11
    """a temporary sub-channel within a GUILD_TEXT or GUILD_FORUM channel"""
    PRIVATE_THREAD = 12
    """a temporary sub-channel within a GUILD_TEXT channel that is only viewable by those 
    invited and those with the MANAGE_THREADS permission"""
    GUILD_STAGE_VOICE = 13
    """a voice channel for hosting events with an audience"""
    GUILD_DIRECTORY = 14
    """the channel in a hub containing the listed servers"""
    GUILD_FORUM = 15
    """Channel that can only contain threads"""


class ComponentType(IntEnum):
    """Component types.

    see https://discord.com/developers/docs/interactions/message-components#component-object-component-types
    """

    ActionRow = 1
    """Container for other components"""
    Button = 2
    """Button object"""
    StringSelect = 3
    """Select menu for picking from defined text options"""
    TextInput = 4
    """TextSegment input object"""
    UserInput = 5
    """Select menu for users"""
    RoleSelect = 6
    """Select menu for roles"""
    MentionableSelect = 7
    """Select menu for mentionables (users and roles)"""
    ChannelSelect = 8
    """Select menu for channels"""


class ConnectionServiceType(StrEnum):
    """Connection service type.

    see https://discord.com/developers/docs/resources/user#connection-object-services"""

    Battle_net = "battlenet"
    eBay = "ebay"
    Epic_Games = "epicgames"
    Facebook = "facebook"
    GitHub = "gitHub"
    Instagram = "instagram"
    League_of_Legends = "leagueoflegends"
    PayPal = "payPal"
    PlayStation_Network = "playstation"
    Reddit = "reddit"
    Riot_Games = "riotgames"
    Spotify = "spotify"
    Skype = "skype"
    Steam = "steam"
    TikTok = "tiktok"
    Twitch = "twitch"
    Twitter = "twitter"
    Xbox_Live = "xbox"
    YouTube = "youtube"


class DefaultMessageNotificationLevel(IntEnum):
    """Default message notification level.

    see https://discord.com/developers/docs/resources/guild#guild-object-default-message-notification-level
    """

    ALL_MESSAGES = 0
    """members will receive notifications for all messages by default"""
    ONLY_MENTIONS = 1
    """members will receive notifications only for messages that @mention them by default"""


class EmbedTypes(StrEnum):
    """
    Embed types.

    see https://discord.com/developers/docs/resources/channel#embed-object-embed-types
    """

    rich = "rich"
    """generic embed rendered from embed attributes"""
    image = "image"
    """image embed"""
    video = "video"
    """video embed"""
    gifv = "gifv"
    """animated gif image embed rendered as a video embed"""
    article = "article"
    """article embed"""
    link = "link"
    """link embed"""


class ExplicitContentFilterLevel(IntEnum):
    """Explicit content filter level.

    see https://discord.com/developers/docs/resources/guild#guild-object-explicit-content-filter-level
    """

    DISABLED = 0
    """media content will not be scanned"""
    MEMBERS_WITHOUT_ROLES = 1
    """media content sent by members without roles will be scanned"""
    ALL_MEMBERS = 2
    """media content sent by all members will be scanned"""


class ForumLayoutTypes(IntEnum):
    """Forum layout types.

    see https://discord.com/developers/docs/resources/channel#channel-object-forum-layout-types
    """

    NOT_SET = 0
    """No default has been set for forum channel"""
    LIST_VIEW = 1
    """Display posts as a list"""
    GALLERY_VIEW = 2
    """Display posts as a collection of tiles"""


class GuildFeature(StrEnum):
    """Guild feature.

    see https://discord.com/developers/docs/resources/guild#guild-object-guild-features
    """

    ANIMATED_BANNER = "ANIMATED_BANNER"
    """guild has access to set an animated guild banner image"""
    ANIMATED_ICON = "ANIMATED_ICON"
    """guild has access to set an animated guild icon"""
    APPLICATION_COMMAND_PERMISSIONS_V2 = "APPLICATION_COMMAND_PERMISSIONS_V2"
    """guild is using the old permissions configuration behavior"""
    AUTO_MODERATION = "AUTO_MODERATION"
    """guild has set up auto moderation rules"""
    BANNER = "BANNER"
    """guild has access to set a guild banner image"""
    COMMUNITY = "COMMUNITY"
    """guild can enable welcome screen, Membership Screening, 
    stage channels and discovery, and receives community updates"""
    CREATOR_MONETIZABLE_PROVISIONAL = "CREATOR_MONETIZABLE_PROVISIONAL"
    """guild has enabled monetization"""
    CREATOR_STORE_PAGE = "CREATOR_STORE_PAGE"
    """guild has enabled the role subscription promo page"""
    DEVELOPER_SUPPORT_SERVER = "DEVELOPER_SUPPORT_SERVER"
    """guild has been set as a support server on the App Directory"""
    DISCOVERABLE = "DISCOVERABLE"
    """guild is able to be discovered in the directory"""
    FEATURABLE = "FEATURABLE"
    """guild is able to be featured in the directory"""
    INVITES_DISABLED = "INVITES_DISABLED"
    """guild has paused invites, preventing new users from joining"""
    INVITE_SPLASH = "INVITE_SPLASH"
    """guild has access to set an invite splash background"""
    MEMBER_VERIFICATION_GATE_ENABLED = "MEMBER_VERIFICATION_GATE_ENABLED"
    """guild has enabled Membership Screening"""
    MORE_STICKERS = "MORE_STICKERS"
    """guild has increased custom sticker slots"""
    NEWS = "NEWS"
    """guild has access to create announcement channels"""
    PARTNERED = "PARTNERED"
    """guild is partnered"""
    PREVIEW_ENABLED = "PREVIEW_ENABLED"
    """guild can be previewed before joining via Membership Screening or the directory"""
    ROLE_ICONS = "ROLE_ICONS"
    """guild is able to set role icons"""
    ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE = (
        "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE"
    )
    """guild has role subscriptions that can be purchased"""
    ROLE_SUBSCRIPTIONS_ENABLED = "ROLE_SUBSCRIPTIONS_ENABLED"
    """guild has enabled role subscriptions"""
    TICKETED_EVENTS_ENABLED = "TICKETED_EVENTS_ENABLED"
    """guild has enabled ticketed events"""
    VANITY_URL = "VANITY_URL"
    """guild has access to set a vanity URL"""
    VERIFIED = "VERIFIED"
    """guild is verified"""
    VIP_REGIONS = "VIP_REGIONS"
    """guild has access to set 384kbps bitrate in voice (previously VIP voice servers)"""
    WELCOME_SCREEN_ENABLED = "WELCOME_SCREEN_ENABLED"
    """	guild has enabled the welcome screen"""


class GuildMemberFlags(IntFlag):
    """Guild member flags.

    see https://discord.com/developers/docs/resources/guild#guild-member-object-guild-member-flags
    """

    DID_REJOIN = 1 << 0
    """Member has left and rejoined the guild"""
    COMPLETED_ONBOARDING = 1 << 1
    """Member has completed onboarding"""
    BYPASSES_VERIFICATION = 1 << 2
    """Member is exempt from guild verification requirements"""
    STARTED_ONBOARDING = 1 << 3
    """Member has started onboarding"""


class GuildNSFWLevel(IntEnum):
    """Guild NSFW level.

    see https://discord.com/developers/docs/resources/guild#guild-object-guild-nsfw-level
    """

    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class GuildScheduledEventEntityType(IntEnum):
    """Guild Scheduled Event Entity Type

    see https://discord.com/developers/docs/resources/guild-scheduled-event#guild-scheduled-event-object-guild-scheduled-event-entity-types
    """

    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3


class GuildScheduledEventPrivacyLevel(IntEnum):
    """Guild Scheduled Event Privacy Level

    see https://discord.com/developers/docs/resources/guild-scheduled-event#guild-scheduled-event-object-guild-scheduled-event-privacy-level
    """

    GUILD_ONLY = 2


class GuildScheduledEventStatus(IntEnum):
    """Guild Scheduled Event Status

    Once status is set to COMPLETED or CANCELED, the status can no longer be updated.

    see https://discord.com/developers/docs/resources/guild-scheduled-event#guild-scheduled-event-object-guild-scheduled-event-status
    """

    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4


class IntegrationExpireBehaviors(IntEnum):
    """Integration Expire Behaviors

    see https://discord.com/developers/docs/resources/guild#integration-object-integration-expire-behaviors
    """

    RemoveRole = 0
    Kick = 0


class InteractionType(IntEnum):
    """Interaction type.

    see https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type
    """

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionCallbackType(IntEnum):
    """Interaction callback type.

    see https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-type
    """

    PONG = 1
    """ACK a Ping"""
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    """respond to an interaction with a message"""
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    """ACK an interaction and edit a response later, the user sees a loading state"""
    DEFERRED_UPDATE_MESSAGE = 6
    """for components, ACK an interaction and edit the original message later; 
    the user does not see a loading state"""
    UPDATE_MESSAGE = 7
    """for components, edit the message the component was attached to.
    Only valid for component-based interactions"""
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    """respond to an autocomplete interaction with suggested choices"""
    MODAL = 9
    """respond to an interaction with a popup modal.
    Not available for MODAL_SUBMIT and PING interactions."""


class InviteTargetType(IntEnum):
    """Invite target type.

    see https://discord.com/developers/docs/resources/invite#invite-object-invite-target-types
    """

    STREAM = 1
    EMBEDDED_APPLICATION = 2


class KeywordPresetType(IntEnum):
    """Keyword preset type.

    see https://discord.com/developers/docs/resources/auto-moderation#auto-moderation-rule-object-keyword-preset-types
    """

    PROFANITY = 1
    """words that may be considered forms of swearing or cursing"""
    SEXUAL_CONTENT = 2
    """"words that refer to sexually explicit behavior or activity"""
    SLURS = 3
    """personal insults or words that may be considered hate speech"""


class MessageActivityType(IntEnum):
    """Message activity type.

    see https://discord.com/developers/docs/resources/channel#message-object-message-activity-types
    """

    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class MessageFlag(IntFlag):
    """Message flags.

    see https://discord.com/developers/docs/resources/channel#message-object-message-flags
    """

    CROSSPOSTED = 1 << 0
    """this message has been published to subscribed channels (via Channel Following)"""
    IS_CROSSPOST = 1 << 1
    """this message originated from a message in another channel (via Channel Following)"""
    SUPPRESS_EMBEDS = 1 << 2
    """do not include any embeds when serializing this message"""
    SOURCE_MESSAGE_DELETED = 1 << 3
    """the source message for this crosspost has been deleted (via Channel Following)"""
    URGENT = 1 << 4
    """this message came from the urgent message system"""
    HAS_THREAD = 1 << 5
    """this message has an associated thread, with the same id as the message"""
    EPHEMERAL = 1 << 6
    """this message is only visible to the user who invoked the Interaction"""
    LOADING = 1 << 7
    """this message is an Interaction Response and the bot is "thinking" """
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8
    """this message failed to mention some roles and add their members to the thread"""
    SUPPRESS_NOTIFICATIONS = 1 << 12
    """	this message will not trigger push and desktop notifications"""


class MessageType(IntEnum):
    """Type REPLY(19) and CHAT_INPUT_COMMAND(20) are only available in API v8 and above.
    In v6, they are represented as type DEFAULT(0).
    Additionally, type THREAD_STARTER_MESSAGE(21) is only available in API v9 and above.

    see https://discord.com/developers/docs/resources/channel#message-object-message-types
    """

    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    USER_JOIN = 7
    GUILD_BOOST = 8
    GUILD_BOOST_TIER_1 = 9
    GUILD_BOOST_TIER_2 = 10
    GUILD_BOOST_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23
    AUTO_MODERATION_ACTION = 24
    ROLE_SUBSCRIPTION_PURCHASE = 25
    INTERACTION_PREMIUM_UPSELL = 26
    STAGE_START = 27
    STAGE_END = 28
    STAGE_SPEAKER = 29
    STAGE_TOPIC = 31
    GUILD_APPLICATION_PREMIUM_SUBSCRIPTION = 32


class MembershipState(IntEnum):
    """Membership state.

    see https://discord.com/developers/docs/topics/teams#data-models-membership-state-enum
    """

    INVITED = 1
    ACCEPTED = 2


class MFALevel(IntEnum):
    """MFA level.

    see https://discord.com/developers/docs/resources/guild#guild-object-mfa-level"""

    NONE = 0
    """guild has no MFA/2FA requirement for moderation actions"""
    ELEVATED = 1
    """guild has a 2FA requirement for moderation actions"""


class MutableGuildFeature(StrEnum):
    """Mutable guild feature.

    see https://discord.com/developers/docs/resources/guild#guild-object-mutable-guild-features
    """

    COMMUNITY = "COMMUNITY"
    """Enables Community Features in the guild"""
    INVITES_DISABLED = "INVITES_DISABLED"
    """Pauses all invites/access to the server"""
    DISCOVERABLE = "DISCOVERABLE"
    """Enables discovery in the guild, making it publicly listed"""


class OnboardingPromptType(IntEnum):
    """Onboarding prompt type.

    see https://discord.com/developers/docs/resources/guild#guild-onboarding-object-prompt-types
    """

    MULTIPLE_CHOICE = 0
    DROPDOWN = 1


class OverwriteType(IntEnum):
    """Overwrite type.

    see https://discord.com/developers/docs/resources/channel#overwrite-object"""

    ROLE = 0
    MEMBER = 1


class PremiumTier(IntEnum):
    """Premium tier.

    see https://discord.com/developers/docs/resources/guild#guild-object-premium-tier"""

    NONE = 0
    """guild has not unlocked any Server Boost perks"""
    TIER_1 = 1
    """guild has unlocked Server Boost level 1 perks"""
    TIER_2 = 2
    """guild has unlocked Server Boost level 2 perks"""
    TIER_3 = 3
    """guild has unlocked Server Boost level 3 perks"""


class PremiumType(IntEnum):
    """Premium types denote the level of premium a user has.
    Visit the Nitro page to learn more about the premium plans we currently offer.

    see https://discord.com/developers/docs/resources/user#user-object-premium-types"""

    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3


class PresenceStatus(StrEnum):
    """Presence Status

    see https://discord.com/developers/docs/topics/gateway-events#presence-update-presence-update-event-fields
    """

    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"
    OFFLINE = "offline"


class SortOrderTypes(IntEnum):
    """Sort order types.

    see https://discord.com/developers/docs/resources/channel#channel-object-sort-order-types
    """

    LATEST_ACTIVITY = 0
    """Sort forum posts by activity"""
    CREATION_DATE = 1
    """Sort forum posts by creation time (from most recent to oldest)"""


class StagePrivacyLevel(IntEnum):
    """Stage Privacy Level

    see https://discord.com/developers/docs/resources/stage-instance#stage-instance-object-privacy-level
    """

    PUBLIC = 1
    """The Stage instance is visible publicly. (deprecated)"""
    GUILD_ONLY = 2
    """The Stage instance is visible to only guild members."""


class StickerFormatType(IntEnum):
    """Sticker format type.

    see https://discord.com/developers/docs/resources/sticker#sticker-object-sticker-format-types
    """

    PNG = 1
    APNG = 2
    LOTTIE = 3
    GIF = 4


class StickerType(IntEnum):
    """Sticker type.

    see https://discord.com/developers/docs/resources/sticker#sticker-object-sticker-types
    """

    STANDARD = 1
    """an official sticker in a pack, part of Nitro or in a removed purchasable pack"""
    GUILD = 2
    """a sticker uploaded to a guild for the guild's members"""


class SystemChannelFlags(IntFlag):
    """System channel flags.

    see https://discord.com/developers/docs/resources/guild#guild-object-system-channel-flags
    """

    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    """Suppress member join notifications"""
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    """Suppress server boost notifications"""
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    """Suppress server setup tips"""
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3
    """Hide member join sticker reply buttons"""
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATIONS = 1 << 4
    """Suppress role subscription purchase and renewal notifications"""
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATION_REPLIES = 1 << 5
    """Hide role subscription sticker reply buttons"""


class TextInputStyle(IntEnum):
    """TextSegment input style.

    see https://discord.com/developers/docs/interactions/message-components#text-input-object-text-input-styles
    """

    Short = 1
    """Single-line input"""
    Paragraph = 2
    """Multi-line input"""


class TimeStampStyle(Enum):
    """Timestamp style.

    see https://discord.com/developers/docs/reference#message-formatting-timestamp-styles
    """

    ShortTime = "t"
    """16:20"""
    LongTime = "T"
    """16:20:30"""
    ShortDate = "d"
    """20/04/2021"""
    LongDate = "D"
    """20 April 2021"""
    ShortDateTime = "f"
    """20 April 2021 16:20"""
    LongDateTime = "F"
    """Tuesday, 20 April 2021 16:20"""
    RelativeTime = "R"
    """2 months ago"""


class TriggerType(IntEnum):
    """Trigger type.

    see https://discord.com/developers/docs/resources/auto-moderation#auto-moderation-rule-object-trigger-types
    """

    KEYWORD = 1
    """check if content contains words from a user defined list of keywords"""
    SPAM = 3
    """check if content represents generic spam"""
    KEYWORD_PRESET = 4
    """check if content contains words from internal pre-defined wordsets"""
    MENTION_SPAM = 5
    """check if content contains more unique mentions than allowed"""


class UpdatePresenceStatusType(StrEnum):
    """Update Presence Status type.

    see https://discord.com/developers/docs/topics/gateway-events#update-presence-status-types
    """

    online = "online"
    """Online"""
    dnd = "dnd"
    """Do Not Disturb"""
    idle = "idle"
    """AFK"""
    invisible = "invisible"
    """Invisible and shown as offline"""
    offline = "offline"
    """	Offline"""


class UserFlags(IntFlag):
    """User flags denote certain attributes about a user.
    These flags are only available to bots.

    see https://discord.com/developers/docs/resources/user#user-object-user-flags"""

    STAFF = 1 << 0
    """Discord Employee"""
    PARTNER = 1 << 1
    """Partnered Server Owner"""
    HYPESQUAD = 1 << 2
    """HypeSquad Events Member"""
    BUG_HUNTER_LEVEL_1 = 1 << 3
    """Bug Hunter Level 1"""
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    """House Bravery Member"""
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    """House Brilliance Member"""
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    """House Balance Member"""
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    """Early Nitro Supporter"""
    TEAM_PSEUDO_USER = 1 << 10
    """User is a team"""
    BUG_HUNTER_LEVEL_2 = 1 << 14
    """Bug Hunter Level 2"""
    VERIFIED_BOT = 1 << 16
    """Verified Bot"""
    VERIFIED_DEVELOPER = 1 << 17
    """Early Verified Bot Developer"""
    CERTIFIED_MODERATOR = 1 << 18
    """Moderator Programs Alumni"""
    BOT_HTTP_INTERACTIONS = 1 << 19
    """Bot uses only HTTP interactions and is shown in the online member list"""
    ACTIVE_DEVELOPER = 1 << 22
    """User is an Active Developer"""


class VerificationLevel(IntEnum):
    """Verification level.

    see https://discord.com/developers/docs/resources/guild#guild-object-verification-level
    """

    NONE = 0
    """unrestricted"""
    LOW = 1
    """must have verified email on account"""
    MEDIUM = 2
    """must be registered on Discord for longer than 5 minutes"""
    HIGH = 3
    """must be a member of the server for longer than 10 minutes"""
    VERY_HIGH = 4
    """must have a verified phone number"""


class VideoQualityMode(IntEnum):
    """Video quality mode.

    see https://discord.com/developers/docs/resources/channel#channel-object-video-quality-modes
    """

    AUTO = 1
    """Discord chooses the quality for optimal performance"""
    FULL = 2
    """720p"""


class VisibilityType(IntEnum):
    """Visibility type.

    see https://discord.com/developers/docs/resources/user#connection-object-visibility-types
    """

    NONE = 0
    """invisible to everyone except the user themselves"""
    EVERYONE = 1
    """visible to everyone"""


class WebhookType(IntEnum):
    """Webhook type.

    see https://discord.com/developers/docs/resources/webhook#webhook-object-webhook-types
    """

    Incoming = 1
    """	Incoming Webhooks can post messages to channels with a generated token"""
    Channel_Follower = 2
    """	Channel Follower Webhooks are internal webhooks used with Channel Following to post new messages into channels"""
    Application = 3
    """Application webhooks are webhooks used with Interactions"""


__all__ = [
    "ActivityAssetImage",
    "ActivityFlags",
    "ActivityType",
    "ApplicationCommandOptionType",
    "ApplicationCommandPermissionsType",
    "ApplicationCommandType",
    "ApplicationFlag",
    "ApplicationRoleConnectionMetadataType",
    "AllowedMentionType",
    "AuditLogEventType",
    "AutoModerationActionType",
    "AutoModerationRuleEventType",
    "ButtonStyle",
    "ChannelFlags",
    "ChannelType",
    "ComponentType",
    "ConnectionServiceType",
    "DefaultMessageNotificationLevel",
    "EmbedTypes",
    "ExplicitContentFilterLevel",
    "ForumLayoutTypes",
    "GuildFeature",
    "GuildMemberFlags",
    "GuildNSFWLevel",
    "GuildScheduledEventEntityType",
    "GuildScheduledEventPrivacyLevel",
    "GuildScheduledEventStatus",
    "IntegrationExpireBehaviors",
    "InteractionType",
    "InteractionCallbackType",
    "InviteTargetType",
    "KeywordPresetType",
    "MessageActivityType",
    "MessageFlag",
    "MessageType",
    "MembershipState",
    "MFALevel",
    "MutableGuildFeature",
    "OnboardingPromptType",
    "OverwriteType",
    "PremiumTier",
    "PremiumType",
    "PresenceStatus",
    "SortOrderTypes",
    "StagePrivacyLevel",
    "StickerFormatType",
    "StickerType",
    "SystemChannelFlags",
    "TextInputStyle",
    "TimeStampStyle",
    "TriggerType",
    "UpdatePresenceStatusType",
    "UserFlags",
    "VerificationLevel",
    "VideoQualityMode",
    "VisibilityType",
    "WebhookType",
]
