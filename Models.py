from typing import Tuple
from Sqlbd import init


@init
class DataBD_yam:
    pattern: str  # 0 mail, 1 yandex
    id: str
    title: str
    url: str
    time: int



@init
class DataUserBD_yam:
    user_id: int
    time: int
    msg: str


@init
class Answer_yam:
    id: int
    qid: int
    state: int
    answer_count: int
    comment_count: int


@init
class Comment_yam:
    id: int  # cmid
    qid: int
    aid: int
    time_add: int
    text: str
    nick: str
    uid: int



@init
class UserDataBD:
    id: int
    fname: str
    lname: str
    gender: int
    joining: int
    bday: int
    group_id: int


@init
class CoverBD:
    group_id: int
    post_id: str
    user_id: str
    time_action: int
    type_action: int
    count: int


@init
class QuestBD:
    id: int
    point: int


@init
class MailBD:
    id: int
    id_group: int


@init
class ChatBD:
    id: str
    id_block: str


@init
class BilionBD:
    id: int
    step: int
    point: int
    lvl: int


