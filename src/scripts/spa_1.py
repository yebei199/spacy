import tempfile
import webbrowser
from pathlib import Path
from unittest.mock import patch

import spacy
from attrs import define, field
from spacy import displacy


@define
class SpaCy1:
    # 加载英语模型
    nlp = field(factory=lambda: spacy.load('en_core_web_sm'))

    def generate_dependency_graph(self, text):
        """生成句子的依存关系图"""
        doc = self.nlp(text)
        # 生成完整HTML格式的依赖图 (page=True 包含官方样式)
        html = displacy.render(doc, style='dep', page=True, jupyter=False)

        # 保存为HTML临时文件
        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        # 使用 standard URI 格式打开，确保通过浏览器而不是文件管理器打开
        file_uri = Path(tmp_name).as_uri()
        print(f'Opening Dependency Graph in browser: {file_uri}')
        webbrowser.open(file_uri)

    def generate_entity_graph(self, text):
        """生成句子的命名实体图"""
        doc = self.nlp(text)
        # 生成完整HTML格式的实体图 (page=True 包含官方样式)
        html = displacy.render(doc, style='ent', page=True, jupyter=False)

        # 保存为HTML临时文件
        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        # 使用 standard URI 格式打开
        file_uri = Path(tmp_name).as_uri()
        print(f'Opening Entity Graph in browser: {file_uri}')
        webbrowser.open(file_uri)


class Test1:
    obj = SpaCy1()

    def test_h3_upload(self):
        assert 1

    def test_dependency_parsing(self):
        # 示例：生成句子的语法图
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        # Mock webbrowser.open to prevent opening browser during test
        self.obj.generate_dependency_graph(sentence)

    def test_entity_recognition(self):
        # 示例：生成句子的命名实体图
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        # Mock webbrowser.open to prevent opening browser during test
        with patch('webbrowser.open'):
            self.obj.generate_entity_graph(sentence)
