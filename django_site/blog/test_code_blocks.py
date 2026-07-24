from django.test import TestCase

from blog.markdown_utils import render_markdown


class CodeBlockEnhancementTests(TestCase):
    def test_fenced_code_gets_chroma_and_copy_button(self):
        html, _ = render_markdown('```python\nprint("hi")\n```')
        self.assertIn('code-block-container', html)
        self.assertIn('copy-code-btn', html)
        self.assertIn('class="chroma"', html)
        self.assertIn('class="nb"', html)

    def test_language_label_in_header(self):
        html, _ = render_markdown('```yaml\nkey: value\n```')
        self.assertIn('YAML', html)
