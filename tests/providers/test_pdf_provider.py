import pytest
from unittest.mock import patch


@pytest.mark.config({"page_range": [0]})
def test_pdf_provider(doc_provider):
    assert len(doc_provider) == 12
    assert doc_provider.get_images([0], 72)[0].size == (612, 792)
    assert doc_provider.get_images([0], 96)[0].size == (816, 1056)

    page_lines = doc_provider.get_page_lines(0)
    assert len(page_lines) == 85

    spans = page_lines[0].spans
    assert len(spans) == 2
    assert spans[0].text == "Subspace Adversarial Training"
    assert spans[0].font == "NimbusRomNo9L-Medi"
    assert spans[0].formats == ["plain"]


@pytest.mark.config({"page_range": [0, 1, 2]})
def test_get_page_labels_filters_default_sequential(doc_provider):
    # Labels that match str(i + 1) are the default 1-based sequential labels
    # and should be filtered out (treated as "no explicit label")
    with patch.object(type(doc_provider), "get_doc") as mock_get_doc:
        mock_doc = mock_get_doc.return_value.__enter__.return_value
        mock_doc.get_page_label.side_effect = lambda i: str(i + 1)

        labels = doc_provider.get_page_labels()
        assert labels == {}


@pytest.mark.config({"page_range": [0, 1, 2]})
def test_get_page_labels_keeps_explicit_labels(doc_provider):
    # Labels that differ from str(i + 1) are truly explicit and should be kept
    explicit = {0: "i", 1: "ii", 2: "iii"}
    with patch.object(type(doc_provider), "get_doc") as mock_get_doc:
        mock_doc = mock_get_doc.return_value.__enter__.return_value
        mock_doc.get_page_label.side_effect = lambda i: explicit.get(i)

        labels = doc_provider.get_page_labels()
        assert labels == explicit


@pytest.mark.config({"page_range": [0, 1, 2]})
def test_get_page_labels_filters_none(doc_provider):
    # None labels (PDF has no PageLabels tree) should be filtered out
    with patch.object(type(doc_provider), "get_doc") as mock_get_doc:
        mock_doc = mock_get_doc.return_value.__enter__.return_value
        mock_doc.get_page_label.return_value = None

        labels = doc_provider.get_page_labels()
        assert labels == {}


@pytest.mark.config({"page_range": [0, 1, 2]})
def test_get_page_labels_mixed(doc_provider):
    # Mix: some pages have explicit labels, others have default sequential labels
    # Only the explicitly-different labels should be in the result
    def side_effect(i):
        if i == 0:
            return "i"   # explicit Roman numeral, kept
        elif i == 1:
            return "ii"  # explicit Roman numeral, kept
        else:
            return str(i + 1)  # default sequential, filtered out

    with patch.object(type(doc_provider), "get_doc") as mock_get_doc:
        mock_doc = mock_get_doc.return_value.__enter__.return_value
        mock_doc.get_page_label.side_effect = side_effect

        labels = doc_provider.get_page_labels()
        assert labels == {0: "i", 1: "ii"}
        assert 2 not in labels
