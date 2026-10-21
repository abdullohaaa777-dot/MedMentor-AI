from medmentor.bot import format_html, MODES

def test_modes():
    assert len(MODES) >= 5

def test_escapes_html():
    assert "&lt;script&gt;" in format_html("<script>")[0]

def test_removes_markdown():
    output = "".join(format_html("## Dopamin\n**D2** $G_i$ \\rightarrow"))
    assert "**" not in output
    assert "$" not in output
    assert "Gi" in output
    assert "→" in output
