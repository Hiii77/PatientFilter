from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from config import ARTIFACTS_PATH

def setup_ocr_pipeline():
    pipeline_options = PdfPipelineOptions(artifacts_path=ARTIFACTS_PATH)
    pipeline_options.do_ocr = True
    pipeline_options.generate_page_images = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = EasyOcrOptions(
    #     lang=["ch_sim","en"],force_full_page_ocr=True
    # )
    pipeline_options.ocr_options = RapidOcrOptions(force_full_page_ocr = True)
    # pipeline_options.ocr_options = TesseractOcrOptions(
    #     lang=["chi_sim","eng"]
    # )
    pipeline_options.enable_remote_services = True

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

def extract_text_from_pdf(pdf_path, page_range=None):
    """使用 docling 将 PDF 中的关键页码转换为 Markdown 格式并提取文本"""
    try:
        # 使用 docling 仅转换特定页码或全文
        doc_converter = setup_ocr_pipeline()
        if page_range is not None:
            result = doc_converter.convert(pdf_path, page_range=page_range)
        else:
            result = doc_converter.convert(pdf_path)
        markdown_text = result.document.export_to_markdown()
        
        return {
            'success': True,
            'text': markdown_text,
            'message': "PDF 成功转换为 Markdown 格式",
            'is_filtered': page_range is not None
        }
    except Exception as e:
        print(f"PDF 处理出错：{str(e)}")
        return {
            'success': False,
            'text': "",
            'message': f"PDF 处理出错：{str(e)}",
            'is_filtered': False
        }

