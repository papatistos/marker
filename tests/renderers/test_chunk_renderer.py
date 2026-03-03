import pytest

from marker.renderers.chunk import ChunkRenderer


@pytest.mark.config({"page_range": [0]})
def test_chunk_renderer(pdf_document):
    renderer = ChunkRenderer()
    chunk_output = renderer(pdf_document)
    blocks = chunk_output.blocks
    page_info = chunk_output.page_info

    assert len(blocks) == 14
    assert blocks[0].block_type == "SectionHeader"
    assert page_info[0]["bbox"] is not None
    assert page_info[0]["polygon"] is not None

    figure_groups = [block for block in blocks if block.block_type == "FigureGroup"]
    figures = [block for block in blocks if block.block_type == "Figure"]
    captions = [block for block in blocks if block.block_type == "Caption"]

    assert len(figure_groups) == 1
    assert len(figures) == 0
    assert len(captions) == 0

    figure_group = figure_groups[0]
    assert figure_group.images is not None
    assert len(figure_group.images) == 1
    assert "<img src='/page/0/Figure/9'>" in figure_group.html


@pytest.mark.config({"page_range": [0]})
def test_chunk_renderer_page_label(pdf_document):
    pdf_document.page_labels = {0: "i"}
    renderer = ChunkRenderer()
    chunk_output = renderer(pdf_document)

    # All blocks on page 0 should carry the page_label
    assert all(block.page_label == "i" for block in chunk_output.blocks)
    # page_info should include the label
    assert chunk_output.page_info[0]["page_label"] == "i"


@pytest.mark.config({"page_range": [0]})
def test_chunk_renderer_no_page_labels(pdf_document):
    # When no page_labels are set, page_label should be None on blocks
    # and page_info should not contain a page_label key
    renderer = ChunkRenderer()
    chunk_output = renderer(pdf_document)

    assert all(block.page_label is None for block in chunk_output.blocks)
    assert "page_label" not in chunk_output.page_info[0]