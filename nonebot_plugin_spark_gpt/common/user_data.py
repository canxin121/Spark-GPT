from typing import Dict, List, Optional
from bidict import bidict
from pydantic import BaseModel
from pathlib import Path
import json
from utils.utils import generate_uuid
from mytypes import (
    BotInfo,
    BotData,
    CommonUserData,
    CommonUserInfo,
    UserInfo,
    UsersInfo,
)


class CommonUsers(BaseModel):
    """所有用户的信息和数据

    :param path: 用户数据的存储路径
    :type path: Path
    :param user_dict: 用户数据的字典
    :type user_dict: Dict[CommonUserInfo, CommonUserData]
    """

    path: Path = Path() / "data/spark_gpt/common"
    user_dict: Dict[CommonUserInfo, CommonUserData] = {}
    user_links: Dict[CommonUserInfo, UsersInfo] = {}

    def new_user(self):
        """新建一个用户,返回新建的CommonUserInfo"""
        common_userinfo = CommonUserInfo(user_id=generate_uuid())
        key = generate_uuid()
        self.user_dict[common_userinfo] = CommonUserData(bots={}, key=key)
        self.save()
        return common_userinfo

    def get_key(self, common_userinfo: CommonUserInfo):
        return self.user_dict[common_userinfo].key

    def dele_user(self, common_userinfo: CommonUserInfo):
        """删除一个指定的用户"""
        del self.user_dict[common_userinfo]
        self.save()

    def __hash__(self):
        return hash(tuple(self.user_dict.keys()))

    def save_userdata(self, common_userinfo: CommonUserInfo):
        """保存指定用户的信息CommonUserData为JSON文件"""
        data = self.user_dict[common_userinfo].save()
        path = self.path / "common_users" / f"{common_userinfo.user_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        with open(path, "w") as f:
            json.dump(data, f)

    def save(self):
        """将UsersInfo对象保存为JSON文件"""
        data = {}
        for common_userinfo, usersinfo in self.user_links.items():
            data[common_userinfo.save()] = usersinfo.save()
        path = self.path / "user_links.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        with open(path, "w") as f:
            json.dump(data, f)

        for common_userinfo, common_userdata in self.user_dict.items():
            data = common_userdata.save()
            path = self.path / "common_users" / f"{common_userinfo.user_id}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.touch()
            with open(path, "w") as f:
                json.dump(data, f)

    def load(self) -> "CommonUsers":
        """从JSON文件中读取CommonUsers对象"""
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path / "user_links.json", "r") as f:
                data = json.load(f)
            user_links = {}
            user_dict = {}
            for common_userinfo, usersinfo in data.items():
                user_links[CommonUserInfo.load(common_userinfo)] = UsersInfo.load(
                    usersinfo=usersinfo
                )
                with open(
                    self.path / "common_users" / f"{common_userinfo}.json", "r"
                ) as f:
                    data2 = json.load(f)
                user_dict[
                    CommonUserInfo(user_id=common_userinfo)
                ] = CommonUserData.load(data2)

            return user_dict, user_links
        except:
            pass

    def __init__(self, **data):
        """从JSON文件中读取数据并创建CommonUsers对象"""
        super().__init__(**data)
        try:
            user_dict, user_links = self.load()
            self.user_dict.update(user_dict)
            self.user_links.update(user_links)
        except:
            pass


common_userinfo1 = CommonUserInfo(user_id="159753654")
common_userinfo2 = CommonUserInfo(user_id="155656555")
common_users = CommonUsers(
    user_dict={
        common_userinfo1: CommonUserData(
            bots={BotInfo(nickname="sss"): BotData(id="ssss")},
            key="123456789",
            user_id="159753654",
        ),
        common_userinfo2: CommonUserData(
            bots={BotInfo(nickname="aaa"): BotData(id="csacsac")},
            key="9555211",
            user_id="155656555",
        )
    },
    user_links={
        common_userinfo1: UsersInfo(
            users=[
                UserInfo(platform="qq", username="123456"),
                UserInfo(platform="telegram", username="456789"),
            ]
        ),
        common_userinfo2: UsersInfo(
            users=[
                UserInfo(platform="qq", username="654321"),
                UserInfo(platform="telegram", username="6543211"),
            ]
        )
    },
)

common_users.user_dict[common_userinfo1].key = "123456789"
common_users.save_userdata(common_userinfo=common_userinfo1)

common_users.save()
