from typing import Dict
import json
from pathlib import Path
from pydantic import BaseModel
from ...common.mytypes import UserInfo, CommonUserInfo
# from mytypes import UserInfo,CommonUserInfo

class Users(BaseModel):
    """储存平台用户和唯一用户的链接

    :param path: 用户数据的存储路径
    :type path: Path
    :param user_links: 平台用户和唯一用户的链接
    :type user_links: Dict[UserInfo, CommonUserInfo]
    """

    path: Path = Path() / "data/spark_gpt/onebot_v11/user_links.json"

    user_links: Dict[UserInfo, CommonUserInfo] = {}

    def link(self, userinfo: UserInfo, common_userinfo: CommonUserInfo):
        """将传入的Userinfo和CommonUserInfo相链接"""
        self.user_links[userinfo] = common_userinfo
        self.save()

    def save(self):
        """将Users对象保存为JSON文件"""
        data = {}
        for userinfo, common_userinfo in self.user_links.items():
            data[userinfo.save()] = common_userinfo.save()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(data, f)

    def load(self) -> "Users":
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
    def __init__(self, **data):
        """从JSON文件中读取数据并创建CommonUsers对象"""
        super().__init__(**data)
        try:
            saved_data = self.load()
            self.user_links.update(saved_data)
        except:
            pass


users = Users()
