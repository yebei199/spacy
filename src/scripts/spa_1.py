import os
import tempfile
import webbrowser
import spacy
from attrs import define, field
from spacy import displacy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cairosvg import svg2png
from pathlib import Path

@define
class SpaCy1:
    # 加载英语模型
    nlp = field(factory=lambda: spacy.load('en_core_web_sm'))

    def generate_dependency_graph(self, text):
        """生成句子的依存关系图"""
        doc = self.nlp(text)
        # 生成SVG格式的依赖图
        svg = displacy.render(doc, style='dep', jupyter=False)

        # 将SVG转换为PNG再显示
        # 使用 delete=False 因为我们需要在 block 关闭后手动读取和删除
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_name = tmp_file.name
        
        try:
            # 写入PNG内容
            svg2png(bytestring=svg.encode('utf-8'), write_to=tmp_name)
            
            # 读取并显示
            img = mpimg.imread(tmp_name)
            plt.figure(figsize=(12, 6))
            plt.imshow(img)
            plt.axis('off')
            plt.title('Dependency Graph')
            plt.tight_layout()
            
            # 弹窗显示，阻塞直到关闭
            plt.show()
        finally:
            # 关闭窗口后删除临时文件
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def generate_entity_graph(self, text):
        """生成句子的命名实体图"""
        doc = self.nlp(text)
        # 生成HTML格式的实体图 (style='ent' 产出 HTML)
        html = displacy.render(doc, style='ent', jupyter=False)

        # 保存为HTML临时文件
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(html)
            tmp_name = tmp_file.name

        # 在浏览器中打开
        # 注意：浏览器打开是异步的，无法精确捕获"关闭"事件，
        # 因此这里不自动删除文件，以免浏览器加载前文件被删。
        print(f"Opening Entity Graph in browser: {tmp_name}")
        webbrowser.open(f'file://{tmp_name}')


class Test1:
    obj = SpaCy1()

    def test_h3_upload(self):
        assert 1

    def test_dependency_parsing(self):
        # 示例：生成句子的语法图
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        from unittest.mock import patch
        # Mock plt.show to prevent blocking
        with patch('matplotlib.pyplot.show'):
            self.obj.generate_dependency_graph(sentence)

    def test_entity_recognition(self):
        # 示例：生成句子的命名实体图
        sentence = 'Apple is looking at buying U.K. startup for $1 billion'
        from unittest.mock import patch
        # Mock webbrowser.open to prevent opening browser during test
        with patch('webbrowser.open'):
            self.obj.generate_entity_graph(sentence)