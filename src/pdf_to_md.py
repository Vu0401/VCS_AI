from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter

def convert_pdf_to_markdown(input_pdf: str, output_md: str):
    """
    Chuyển đổi file PDF sang file Markdown.
    
    Args:
        input_pdf (str): Đường dẫn tới file PDF cần chuyển đổi.
        output_md (str): Đường dẫn tới file Markdown đầu ra.
    """
    # Thiết lập các tùy chọn cho pipeline
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.ocr_options.use_gpu = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["en"]

    # Tạo đối tượng DocumentConverter
    converter = DocumentConverter()

    # Chuyển đổi file PDF
    converted_doc = converter.convert(input_pdf)

    # Xuất nội dung ra file Markdown
    markdown_content = converted_doc.document.export_to_markdown()

    # Lưu nội dung vào file Markdown
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"File {output_md} đã được lưu thành công!")

if __name__ == "__main__":
    # Danh sách các cặp đường dẫn PDF đầu vào và Markdown đầu ra
    files = [
        ("./data/CEH_Certified_Ethical_Hacker_Bundle,_5th_Edition_Matt_Walker_2022-1.pdf", "./data/CEH_Certified_Ethical_Hacker_Bundle,_5th_Edition_Matt_Walker_2022-1.md"),
        ("./data/CEH_v10_EC-Council_Certified_E-IP_Specialist-1.pdf", "./data/CEH_v10_EC-Council_Certified_E-IP_Specialist-1.md"),
        ("./data/Sybex_CEH_v10_Certified_Ethical.pdf", "./data/sybex_md_parser.md"),
    ]

    # Chuyển đổi từng file
    for input_pdf, output_md in files:
        convert_pdf_to_markdown(input_pdf, output_md)
        print(f"Converted {input_pdf} to {output_md}")