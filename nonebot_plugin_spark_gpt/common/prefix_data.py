from pydantic import BaseModel, Field
from pathlib import Path
from nonebot import logger
import json


class Prefixs(BaseModel):
    path: Path = Field(
        Path() / "data/spark_gpt/common/prefixs.json", description="储存prefixs.json的路径"
    )
    prefixs: dict = Field({}, description="储存所有前缀")

    def __init__(self, **data):
        super().__init__(**data)
        self.path: Path = Path() / "data/spark_gpt/common/prefixs.json"
        self.prefixs: dict = {
            "EitherChoice": '请记住下面的要求:\nA是指先说的事物,而B是指后说的事物\n我的输入将是"对比A和B"\n要求结果必须是   A比B好\n你的输出的格式是一个markdown格式的表格\nmarkdown表格要求如下\n| Aspect | 👍A | 👎B |\n| --- | --- | --- |\n| 方面1 | 😍A的优势| 🤡B的劣势|\n| 方面2 | 🦊A的优势| 👾B的劣势|\n如此重复7行,表情可以自行替换(😊😂❤️😍😒🙌🤞✌️💖😢🤷‍♂️🤷‍♀️🎶😎🫥😶😑😶‍🌫️🤐😒🤤😌😝😪😛🙃🙁😲😰😬🤯🙁🤡🤭🥸🤢👾😸🙉🙊👾😈☠️🦊🐻‍❄️🐗)，增加多样性\n对比的内容要字数足够多，理由足够充分\n对比的内容要字数足够多\n要求结果必须是   A比B好\n记住要7个项目的对比,生成7行.\n以下是我的输入:',
        }
        try:
            self.load()
        except Exception as e:
            # logger.error(str(e))
            pass

    def show_prefix(self, prefix_name: str):
        """获取指定prefix的前缀内容"""
        try:
            prefix = self.prefixs[prefix_name]
            return prefix
        except KeyError:
            raise Exception("没有这个前缀名")

    def show_list(self):
        """获取所有的prefixs的名称"""
        prefix_list_str = "所有前缀如下:\n\n| 前缀名称 |\n| --- |\n"
        for key in self.prefixs.keys():
            prefix_list_str += f"| {key} |\n"
        prefix_list_str += "\n"
        return prefix_list_str

    def change(self, prefix_name: str, prefix: str):
        if prefix_name in self.prefixs.keys():
            self.prefixs[prefix_name] = prefix
            self.save()
        else:
            raise Exception("没有这个前缀名")

    def rename(self, old_name: str, new_name: str):
        """将prefixs中的原有名字修改成新名字"""
        if old_name not in self.prefixs:
            raise Exception("没有这个前缀名")
        elif new_name in self.prefixs:
            raise Exception("前缀名重复,新前缀名已存在")
        else:
            self.prefixs = {
                new_name if key == old_name else key: value
                for key, value in self.prefixs.items()
            }
            self.save()

    def add(self, prefix_name: str, prefix: str):
        """向prefixs中添加前缀"""
        self.prefixs[prefix_name] = prefix
        self.save()

    def delete(self, prefix_name: str):
        """删除prefixs中的前缀"""
        try:
            del self.prefixs[prefix_name]
        except KeyError:
            logger.error("没有这个前缀名")
            raise Exception("没有这个前缀名")
        except Exception as e:
            logger.error(str(e))
            raise e
        self.save()

    def load(self):
        """从JSON文件中读取prefixs"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.prefixs = json.load(f)
        except Exception as e:
            raise e

    def save(self):
        """将prefixs保存为JSON文件"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.prefixs, f, ensure_ascii=False)


prefixs = Prefixs()
