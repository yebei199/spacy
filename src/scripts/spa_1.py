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

    # 色彩配置 (Color Configuration)
    # 用于 POS Tag 可视化 (style='ent' manual mode)
    pos_colors = {
        'VERB': '#64B5F6',  # Blue for Verbs
        'NOUN': '#81C784',  # Green for Nouns
        'PROPN': '#4DB6AC',  # Teal for Proper Nouns
        'ADJ': '#FFB74D',  # Orange for Adjectives
        'ADV': '#FFD54F',  # Amber for Adverbs
        'PRON': '#BA68C8',  # Purple for Pronouns
        'ADP': '#90A4AE',  # Grey for Prepositions
        'AUX': '#7986CB',  # Indigo for Auxiliaries
        'DET': '#E0E0E0',  # Light Grey for Determiners
        'CCONJ': '#A1887F',  # Brown for Conjunctions
        'PUNCT': '#E0E0E0',  # Light Grey for Punctuation
    }

    # Dependency Graph 配置
    dep_options = {
        'compact': False,
        'bg': '#ffffff',
        'color': '#2c3e50',  # Dark Blue-Grey instead of pure black
        'font': 'Source Sans Pro',
        'distance': 100,
    }

    def generate_dependency_graph(self, text):
        """生成句子的依存关系图 (Dependency Parse)"""
        doc = self.nlp(text)

        # 官方 Dependency Visualizer 通常是单色的。
        # 这里应用了自定义的颜色(深灰蓝)和字体配置。
        html = displacy.render(
            doc, style='dep', page=True, jupyter=False, options=self.dep_options
        )

        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        file_uri = Path(tmp_name).as_uri()
        print(f'Opening Dependency Graph in browser: {file_uri}')
        webbrowser.open(file_uri)

    def generate_entity_graph(self, text):
        """生成句子的命名实体图 (Named Entity Recognition)"""
        doc = self.nlp(text)
        # style='ent' 默认自带颜色配置
        html = displacy.render(doc, style='ent', page=True, jupyter=False)

        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        file_uri = Path(tmp_name).as_uri()
        print(f'Opening Entity Graph in browser: {file_uri}')
        webbrowser.open(file_uri)

    def generate_pos_graph(self, text):
        """
        生成词性标注图 (POS Tagging Visualization)
        使用 'ent' 风格来模拟 POS 染色，满足'动词一个颜色, 名词一个颜色'的需求。
        """
        doc = self.nlp(text)

        # 将 POS Tags 转换为实体格式以便使用 displacy 的 ent 模式进行染色
        ents = []
        for token in doc:
            ents.append({
                'start': token.idx,
                'end': token.idx + len(token),
                'label': token.pos_,
            })

        # 构建 manual data
        ex = [
            {'text': text, 'ents': ents, 'title': 'POS Tagging Visualization'}
        ]

        options = {'colors': self.pos_colors}

        html = displacy.render(
            ex,
            style='ent',
            manual=True,
            page=True,
            jupyter=False,
            options=options,
        )

        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        file_uri = Path(tmp_name).as_uri()
        print(f'Opening POS Graph in browser: {file_uri}')
        webbrowser.open(file_uri)


class Test1:
    obj = SpaCy1()

    def test_h3_upload(self):
        assert 1

    def test_dependency_parsing(self):
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        self.obj.generate_dependency_graph(sentence)

    def test_entity_recognition(self):
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        with patch('webbrowser.open'):
            self.obj.generate_entity_graph(sentence)

    def test_pos_graph(self):
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        self.obj.generate_pos_graph(sentence)
