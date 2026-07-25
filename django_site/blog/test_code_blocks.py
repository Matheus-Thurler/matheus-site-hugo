from django.test import SimpleTestCase, TestCase

from blog.markdown_utils import render_markdown


class CodeBlockEnhancementTests(SimpleTestCase):
    def test_fenced_code_gets_chroma_and_copy_button(self):
        html, _ = render_markdown('```python\nprint("hi")\n```')
        self.assertIn('code-block-container', html)
        self.assertIn('copy-code-btn', html)
        self.assertIn('class="chroma"', html)
        self.assertIn('class="nb"', html)

    def test_language_label_in_header(self):
        html, _ = render_markdown('```yaml\nkey: value\n```')
        self.assertIn('YAML', html)

    def test_mermaid_skips_code_block_ui(self):
        html, _ = render_markdown('```mermaid\ngraph TD\nA-->B\n```')
        self.assertNotIn('copy-code-btn', html)
        self.assertIn('class="mermaid"', html)

    def test_hugo_mermaid_shortcode_is_supported(self):
        html, _ = render_markdown('{{< mermaid >}}\nflowchart LR\nA-->B\n{{< /mermaid >}}')
        self.assertIn('class="mermaid"', html)
        self.assertIn('mermaid-diagram', html)
