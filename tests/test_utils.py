import pytest

from pdfwork.utils import fmt_pat


@pytest.mark.parametrize("pat, expect", [
    ("{0:04d}.pdf", "{0:04d}.pdf"),
    ("{}", "{}/{0:04d}.pdf"),
    ("example.pdf", "example{0:04d}.pdf"),
    ("dir", "dir/{0:04d}.pdf"),
])
def test_fmt_pat(pat, expect):
    assert fmt_pat(pat, 1000) == expect