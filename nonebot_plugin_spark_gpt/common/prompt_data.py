from pydantic import BaseModel
from pathlib import Path
from nonebot import logger
import json

class Prompts(BaseModel):
    path: Path = Path() / "data/spark_gpt/common/prompts.json"
    prompts: dict = {
            "prompt1": "This is the first prompt.",
            "prompt2": "This is the second prompt.",
            "prompt3": "This is the third prompt.",
            "prompt4": "This is the fourth prompt.",
            "prompt5": "This is the fifth prompt.",
            "prompt6": "This is the sixth prompt.",
            "prompt7": "This is the seventh prompt.",
            "prompt8": "This is the eighth prompt.",
            "prompt9": "This is the ninth prompt.",
            "prompt10": "This is the tenth prompt."
        }
    def show_prompt(self,prompt_name:str):
        """获取指定prompt的预设内容"""
        try:
            prompt = self.prompts[prompt_name]
            return prompt
        except KeyError:
            raise Exception("没有这个预设名")
    def show_list(self):
        """获取所有的prompts的名称"""
        num_per_line = 2
        prompt_list_str = ""
        for i, key in enumerate(self.prompts.keys()):
            prompt_list_str += "{:02d}. {}\t".format(i+1, key)
            if (i+1) % num_per_line == 0:
                prompt_list_str += "\n"
        if len(self.prompts) % num_per_line != 0:
            prompt_list_str += "\n"
        return prompt_list_str
    def add(self,prompt_name:str,prompt:str):
        """向prompts中添加预设"""
        self.prompts[prompt_name] = prompt
        self.save()
    def delete(self,prompt_name:str):
        """删除prompts中的预设"""
        try:
            del self.prompts[prompt_name]
        except KeyError:
            raise Exception("没有这个预设名")
        self.save()
    def load(self):
        """从JSON文件中读取prompts"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()
        try:
            with open(self.path, "r", encoding='utf-8') as f:
                self.prompts = json.load(f)
        except Exception as e:
            raise e 
    def save(self):
        """将prompts保存为JSON文件"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.prompts, f, ensure_ascii=False)
    def __init__(self, **data):
        """从JSON文件中读取数据并创建CommonUsers对象"""
        super().__init__(**data)
        try:
            self.load()
        except Exception as e:
            logger.error(str(e))
            pass
        
prompts = Prompts()
