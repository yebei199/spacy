import tempfile
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import spacy
from attrs import define, field
from spacy import displacy


@define
class SpaCy1:
    # 加载英语模型
    nlp = field(factory=lambda: spacy.load('en_core_web_sm'))

    # 1. 词性 (POS) 颜色映射
    pos_colors = {
        'VERB': '#E57373',  # Red
        'NOUN': '#64B5F6',  # Blue
        'PROPN': '#4DB6AC',  # Teal
        'ADJ': '#FFB74D',  # Orange
        'ADV': '#FFD54F',  # Amber
        'PRON': '#BA68C8',  # Purple
        'ADP': '#90A4AE',  # Grey
        'AUX': '#7986CB',  # Indigo
        'DET': '#E0E0E0',  # Light Grey
        'CCONJ': '#A1887F',  # Brown
        'PUNCT': '#BDBDBD',  # Grey
        'NUM': '#FFF176',  # Yellow
        'PART': '#E0E0E0',  # Light Grey
        'SYM': '#E0E0E0',  # Light Grey
        'INTJ': '#FF8A65',  # Deep Orange
        'X': '#E0E0E0',  # Light Grey
    }

    # 2. 依存关系 (Dependency Label) 颜色映射
    dep_colors = {
        'nsubj': '#E57373',
        'nsubjpass': '#E57373',
        'csubj': '#E57373',
        'csubjpass': '#E57373',  # Subject: Red
        'dobj': '#64B5F6',
        'pobj': '#64B5F6',
        'attr': '#64B5F6',  # Object/Attribute: Blue
        'amod': '#FFB74D',
        'advmod': '#FFD54F',
        'nummod': '#FFB74D',  # Modifier: Orange/Amber
        'prep': '#90A4AE',  # Preposition: Grey
        'det': '#E0E0E0',  # Determiner: Light Grey
        'cc': '#A1887F',  # Conjunction: Brown
        'conj': '#A1887F',
        'aux': '#7986CB',
        'auxpass': '#7986CB',  # Aux: Indigo
        'root': '#000000',  # Root: Black (Emphasis)
        'punct': '#BDBDBD',  # Punctuation: Grey
        'compound': '#4DB6AC',  # Compound: Teal
        'acl': '#FF8A65',
        'relcl': '#FF8A65',  # Clauses: Deep Orange
    }

    # 默认颜色
    default_dep_color = '#455A64'

    def get_dep_color(self, label):
        """获取依存关系的颜色，如果不匹配则返回默认色"""
        return self.dep_colors.get(label.lower(), self.default_dep_color)

    def colorize_svg(self, svg_content):
        """
        解析并修改 SVG，为单词 (基于 POS) 和线条 (基于 Dependency) 上色。
        """
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError:
            # 如果解析失败，返回原内容
            return svg_content

        ns = {'svg': 'http://www.w3.org/2000/svg'}

        # 1. Colorize Words (Tokens)
        # 查找所有包含单词和TAG的文本节点
        # displacy 结构: <text class="displacy-token"> ... <tspan class="displacy-tag">TAG</tspan> </text>
        for text_node in root.findall(
            ".//svg:text[@class='displacy-token']", ns
        ):
            tspans = text_node.findall('svg:tspan', ns)
            # 通常第一个 tspan 是单词，第二个 tspan 是 POS tag
            if len(tspans) >= 2:
                # 尝试获取 POS Tag (通常在第二个 span)
                # 注意: 有时 span 内容可能有空格，需要 strip
                tag = tspans[1].text.strip() if tspans[1].text else ''

                # 如果匹配到 POS 颜色
                if tag in self.pos_colors:
                    color = self.pos_colors[tag]

                    # 设置主 text 节点的 fill (有些浏览器继承)
                    text_node.set('fill', color)

                    # 强制设置所有 tspan 子节点的 fill，覆盖 currentColor
                    for span in tspans:
                        span.set('fill', color)

        # 2. Colorize Arcs (Dependencies)
        # displacy 结构: <g class="displacy-arrow"> <path class="displacy-arc"/> <text><textPath>LABEL</textPath></text> <path class="displacy-arrowhead"/> </g>
        for arrow_group in root.findall(
            ".//svg:g[@class='displacy-arrow']", ns
        ):
            text_path = arrow_group.find('.//svg:textPath', ns)
            if text_path is not None:
                label = text_path.text.strip() if text_path.text else ''
                color = self.get_dep_color(label)

                # 设置线条颜色
                arc_path = arrow_group.find(
                    ".//svg:path[@class='displacy-arc']", ns
                )
                if arc_path is not None:
                    arc_path.set('stroke', color)

                # 设置箭头颜色
                head_path = arrow_group.find(
                    ".//svg:path[@class='displacy-arrowhead']", ns
                )
                if head_path is not None:
                    head_path.set('fill', color)

                # 设置标签文字颜色
                text_path.set('fill', color)

        return ET.tostring(root, encoding='unicode')

    def generate_dependency_graph(self, text):
        """生成句子的依存关系图 (Dependency Parse) - 彩色增强版"""
        doc = self.nlp(text)

        # 1. 生成基础 SVG (不带 page wrapper，方便 XML 处理)
        svg_content = displacy.render(
            doc, style='dep', page=False, jupyter=False
        )

        # 2. 后处理 SVG 进行上色
        colored_svg = self.colorize_svg(svg_content)

        # 3. 包装成完整 HTML (模拟 page=True 的效果)
        html = f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Colorful Dependency Graph</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                padding: 4rem 2rem;
                direction: ltr;
            }}
            figure {{
                margin-bottom: 6rem;
            }}
        </style>
    </head>
    <body>
        <figure>
            {colored_svg}
        </figure>
    </body>
</html>"""

        # 保存并打开
        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        file_uri = Path(tmp_name).as_uri()
        print(f'Opening Colorful Dependency Graph in browser: {file_uri}')
        webbrowser.open(file_uri)

    def generate_entity_graph(self, text):
        """生成句子的命名实体图"""
        doc = self.nlp(text)
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
        """生成纯词性标注图"""
        doc = self.nlp(text)
        ents = []
        for token in doc:
            ents.append({
                'start': token.idx,
                'end': token.idx + len(token),
                'label': token.pos_,
            })

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
        with patch('webbrowser.open'):
            self.obj.generate_pos_graph(sentence)
