from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
import fitz

class PdfViewerDialog(QDialog):
    # 现有的PdfViewerDialog类
    def __init__(self, pdf_path):
        super().__init__()
        self.setWindowTitle("PDF 浏览器")
        self.setGeometry(100, 100, 800, 600)
        self.selected_pages = set()
        
        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        self.load_pdf_pages(pdf_path)
        
        self.select_button = QPushButton("确认选择")
        self.select_button.clicked.connect(self.accept)
        layout.addWidget(self.select_button)
        
        self.setLayout(layout)

    def load_pdf_pages(self, pdf_path):
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            label = QLabel()
            label.setPixmap(QPixmap.fromImage(image))
            label.mousePressEvent = lambda event, page_num=i: self.toggle_page_selection(event, page_num)
            self.content_layout.addWidget(label)

    def toggle_page_selection(self, event, page_num):
        if page_num in self.selected_pages:
            self.selected_pages.remove(page_num)
        else:
            self.selected_pages.add(page_num)
        self.update_page_highlight(page_num)

    def update_page_highlight(self, page_num):
        item = self.content_layout.itemAt(page_num)
        label = item.widget()
        pixmap = label.pixmap()
        painter = QPainter(pixmap)
        if page_num in self.selected_pages:
            painter.setPen(QColor("blue"))
            painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
        else:
            painter.setPen(QColor("transparent"))
            painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
        painter.end()
        label.setPixmap(pixmap)

    def select_pages(self):
        self.accept()