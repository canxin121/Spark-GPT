import json
from pathlib import Path
from typing import Dict

from pydantic import BaseModel, Field

from ...common.mytypes import UserInfo, CommonUserInfo
from ...common.user_data import common_users


class Users(BaseModel):
    """储存平台用户和唯一用户的链接

    :param path: 用户数据的存储路径
    :type path: Path
    :param user_links: 平台用户和唯一用户的链接
    :type user_links: Dict[UserInfo, CommonUserInfo]
    """

    path: Path = Field(
        Path() / "data/spark_gpt/platforms/nonebot.json", description="用户数据的存储路径"
    )

    user_links: Dict[UserInfo, CommonUserInfo] = Field({}, description="用户链接的字典")

    def __init__(self, **data):
        super().__init__(**data)
        self.path: Path = (
                data.get("path") or Path() / "data/spark_gpt/platforms/nonebot.json"
        )

        self.user_links: Dict[UserInfo, CommonUserInfo] = data.get("user_links") or {}
        try:
            saved_data = self.load()
            self.user_links.update(saved_data)
        except Exception:
            pass

    def link(self, userinfo: UserInfo, common_userinfo: CommonUserInfo):
        """将传入的Userinfo和CommonUserInfo相链接"""
        self.user_links[userinfo] = common_userinfo
        common_users.link_user(common_userinfo, userinfo)
        self.save()

    def save(self):
        """将Users对象保存为JSON文件"""
        data = {}
        for userinfo, common_userinfo in self.user_links.items():
            data[userinfo.save()] = common_userinfo.save()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(data, f)

    def load(self):
        """从JSON文件中读取Users对象"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            finaldata = {}
            for userinfo, user_id in data.items():
                finaldata[UserInfo.load(userinfo)] = CommonUserInfo.load(user_id)
            return finaldata
        except:
            pass


users = Users()
