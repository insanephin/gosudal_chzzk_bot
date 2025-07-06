from pydantic import BaseModel
from typing import List, Dict, Optional


class accountInterlock(BaseModel):
    code: str
    state: str


class accountInfo(BaseModel):
    channelId: str
    channelName: str
    nickname: str


class accessToken(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    expiresIn: Optional[int] = None
    scope: Optional[str] = None


class Event(BaseModel):
    eventType: str
    channelId: str


class sessionInfo(BaseModel):
    sessionKey: str
    connectedDate: str
    disconnectedDate: Optional[str] = None
    subscribedEvents: List[Event]


class sessionCreate(BaseModel):
    url: str


class Badge(BaseModel):
    imageUrl: str


class Profile(BaseModel):
    nickname: str
    verifiedMark: bool
    badges: List[Badge]


class Chat(BaseModel):
    channelId: str
    senderChannelId: str
    profile: Profile
    content: str
    emojis: Dict[str, str]
    messageTime: int
    eventSentAt: str


class Message(BaseModel):
    messageId: str