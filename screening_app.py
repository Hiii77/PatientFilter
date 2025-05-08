from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                           QTextEdit, QFileDialog, QLabel, QHBoxLayout, QSplitter, QDialog, QListWidget, QScrollArea, QStackedLayout, QTextBrowser)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from pdf_viewer import PdfViewerDialog
from ocr_utils import extract_text_from_pdf
from api_utils import extract_criteria_from_text, analyze_patient_criteria, organize_patient_case
import sys
import fitz

class ScreeningApp(QWidget):
    def __init__(self):
        super().__init__()
        self.criteria_text = ""
        self.current_pdf_path = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("临床试验受试者筛查工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板 - 入排标准
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.criteria_label = QLabel("试验方案入排标准")
        left_layout.addWidget(self.criteria_label)
        
        self.criteria_text_edit = QTextEdit()
        left_layout.addWidget(self.criteria_text_edit)
        
        self.load_pdf_button = QPushButton("加载 PDF")
        self.load_pdf_button.clicked.connect(self.load_pdf)
        left_layout.addWidget(self.load_pdf_button)
        
        self.extract_criteria_button = QPushButton("提取入排标准")
        self.extract_criteria_button.clicked.connect(self.extract_criteria)
        left_layout.addWidget(self.extract_criteria_button)
        
        # 在左侧面板添加状态标签
        self.status_label = QLabel("")
        left_layout.addWidget(self.status_label)
        
        left_widget.setLayout(left_layout)
        
        # 右侧面板 - 患者病例
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # 创建标题和切换按钮的水平布局
        title_layout = QHBoxLayout()
        self.case_label = QLabel("患者病例")
        title_layout.addWidget(self.case_label)
        
        # 添加切换显示模式按钮
        self.toggle_view_button = QPushButton("")
        self.toggle_view_button.setFixedSize(12, 12)  # 设置按钮大小为小圆点
        self.toggle_view_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;  /* 橘黄色 */
                border-radius: 6px;  /* 圆角半径等于高度的一半 */
                border: none;
            }
            QPushButton:hover {
                background-color: #FF8C00;  /* 鼠标悬停时颜色变深 */
            }
        """)
        self.toggle_view_button.clicked.connect(self.toggle_view_mode)
        title_layout.addWidget(self.toggle_view_button)
        title_layout.addStretch()  # 添加弹性空间，使按钮靠左
        
        right_layout.addLayout(title_layout)
        
        # 创建堆叠布局用于切换显示模式
        self.case_stack = QStackedLayout()
        
        # 文本编辑模式
        self.case_text_edit = QTextBrowser()
        self.case_text_edit.setOpenExternalLinks(True)  # 允许打开外部链接
        self.case_text_edit.setOpenLinks(True)  # 允许打开链接
        self.case_stack.addWidget(self.case_text_edit)
        
        # PDF显示模式
        pdf_widget = QWidget()
        pdf_layout = QVBoxLayout()
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setWidgetResizable(True)
        self.pdf_content = QWidget()
        self.pdf_layout = QVBoxLayout()
        self.pdf_content.setLayout(self.pdf_layout)
        self.pdf_scroll.setWidget(self.pdf_content)
        pdf_layout.addWidget(self.pdf_scroll)
        pdf_widget.setLayout(pdf_layout)
        self.case_stack.addWidget(pdf_widget)
        
        right_layout.addLayout(self.case_stack)
        
        # 创建按钮区域的水平布局
        buttons_layout = QHBoxLayout()
        
        self.load_case_button = QPushButton("加载病例 PDF")
        self.load_case_button.clicked.connect(self.load_case_pdf)
        buttons_layout.addWidget(self.load_case_button)
        
        # 添加整理病例按钮
        self.organize_case_button = QPushButton("整理病例")
        self.organize_case_button.clicked.connect(self.organize_case)
        self.organize_case_button.setStyleSheet("background-color: #a3e4ff;")
        buttons_layout.addWidget(self.organize_case_button)
        
        right_layout.addLayout(buttons_layout)
        
        self.classify_case_button = QPushButton("分析是否符合入排标准")
        self.classify_case_button.clicked.connect(self.classify_case)
        right_layout.addWidget(self.classify_case_button)
        
        self.result_text_edit = QTextEdit()
        self.result_text_edit.setPlaceholderText("分析结果将显示在这里")
        right_layout.addWidget(self.result_text_edit)
        
        # 添加重启按钮
        self.restart_button = QPushButton("重新开始")
        self.restart_button.clicked.connect(self.restart)
        self.restart_button.setStyleSheet("background-color: #ffb1a3;")  # 设置红色背景
        right_layout.addWidget(self.restart_button)
        
        right_widget.setLayout(right_layout)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def load_pdf(self):
        """选择并加载 PDF"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 PDF", "", "PDF Files (*.pdf)")
        if file_path:
            dialog = PdfViewerDialog(file_path)
            if dialog.exec_() == QDialog.Accepted:
                # 将页码从0开始转换为1开始
                selected_pages = [page + 1 for page in dialog.selected_pages]
                print(f"Selected pages: {selected_pages}")  # 添加调试信息
                
                # 获取页码范围
                if selected_pages:
                    page_range = (min(selected_pages), max(selected_pages))
                    print(f"Page range: {page_range}")  # 打印页码范围
                    result = extract_text_from_pdf(file_path, page_range=page_range)
                    
                    if result['success']:
                        self.criteria_text_edit.setPlainText(result['text'])
                        
                        # 设置状态提示
                        if result['is_filtered']:
                            self.status_label.setText(result['message'])
                            self.status_label.setStyleSheet("color: green;")
                        else:
                            self.status_label.setText(result['message'])
                            self.status_label.setStyleSheet("color: blue;")
                    else:
                        self.status_label.setText(result['message'])
                        self.status_label.setStyleSheet("color: red;")
    
    def extract_criteria(self):
        """提取入排标准"""
        text = self.criteria_text_edit.toPlainText()
        if not text:
            self.status_label.setText("请先加载 PDF 文件！")
            self.status_label.setStyleSheet("color: red;")
            return
            
        self.status_label.setText("正在连接 DeepSeek 服务器，请稍候...")
        self.status_label.setStyleSheet("color: blue;")
        QApplication.processEvents()  # 立即更新界面
        
        success, result = extract_criteria_from_text(text)
        
        if success:
            self.criteria_text = result
            self.criteria_text_edit.setPlainText(self.criteria_text)
            self.status_label.setText("入排标准提取成功！")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"错误：{result}")
            self.status_label.setStyleSheet("color: red;")
    
    def load_case_pdf(self):
        """选择并加载病例 PDF"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择病例 PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_pdf_path = file_path
            
            # 清除现有的PDF内容
            for i in reversed(range(self.pdf_layout.count())): 
                self.pdf_layout.itemAt(i).widget().setParent(None)
            
            # 加载PDF并显示
            try:
                doc = fitz.open(file_path)
                for i in range(len(doc)):
                    page = doc.load_page(i)
                    pix = page.get_pixmap()
                    image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    label = QLabel()
                    label.setPixmap(QPixmap.fromImage(image))
                    self.pdf_layout.addWidget(label)
                doc.close()
            except Exception as e:
                self.status_label.setText(f"加载PDF失败：{str(e)}")
                self.status_label.setStyleSheet("color: red;")
                return
            
            # 右上角患者病例转换全部页面
            result = extract_text_from_pdf(file_path)
            
            if result['success']:
                # 设置Markdown内容
                self.case_text_edit.setMarkdown(result['text'])
                
                # 设置状态提示
                if result['is_filtered']:
                    self.status_label.setText(result['message'])
                    self.status_label.setStyleSheet("color: green;")
                else:
                    self.status_label.setText(result['message'])
                    self.status_label.setStyleSheet("color: blue;")
            else:
                self.status_label.setText(result['message'])
                self.status_label.setStyleSheet("color: red;")

    def toggle_view_mode(self):
        """切换显示模式"""
        if self.case_stack.currentIndex() == 0:  # 当前是文本模式
            if self.current_pdf_path:
                self.case_stack.setCurrentIndex(1)  # 切换到PDF模式
            else:
                self.status_label.setText("请先加载PDF文件！")
                self.status_label.setStyleSheet("color: red;")
        else:  # 当前是PDF模式
            self.case_stack.setCurrentIndex(0)  # 切换到文本模式

    def classify_case(self):
        """分析患者是否符合入排标准"""
        # 获取左侧的入排标准
        criteria = self.criteria_text_edit.toPlainText()
        # 获取右侧的患者病例
        patient_case = self.case_text_edit.toMarkdown()  # 获取Markdown格式的文本
        
        if not criteria:
            self.status_label.setText("请先加载或输入入排标准！")
            self.status_label.setStyleSheet("color: red;")
            return
        
        if not patient_case:
            self.status_label.setText("请先加载病例 PDF 文件！")
            self.status_label.setStyleSheet("color: red;")
            return
        
        self.status_label.setText("正在连接 DeepSeek 服务器，请稍候...")
        self.status_label.setStyleSheet("color: blue;")
        QApplication.processEvents()  # 立即更新界面
        
        # 调用分析函数
        result = analyze_patient_criteria(criteria, patient_case)
        
        if result and not result.startswith("分析失败"):
            self.result_text_edit.setPlainText(result)
            self.status_label.setText("病例分析成功！")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.result_text_edit.setPlainText(result if result else "无返回结果")
            self.status_label.setText("分析失败，请查看详细信息")
            self.status_label.setStyleSheet("color: red;")

    def restart(self):
        """清除所有内容和记忆，重新开始"""
        # 清除左侧面板内容
        self.criteria_text_edit.clear()
        
        # 清除右侧面板内容
        self.case_text_edit.clear()
        self.result_text_edit.clear()
        self.current_pdf_path = None
        
        # 清除PDF显示
        for i in reversed(range(self.pdf_layout.count())): 
            self.pdf_layout.itemAt(i).widget().setParent(None)
        
        self.case_stack.setCurrentIndex(0)  # 切换到文本模式
        
        # 重置状态标签
        self.status_label.setText("已重置所有内容")
        self.status_label.setStyleSheet("color: blue;")
        
        # 重置内部变量
        self.criteria_text = ""

    def organize_case(self):
        """整理患者病例"""
        # 获取右侧的患者病例
        patient_case = self.case_text_edit.toMarkdown()  # 获取Markdown格式的文本
        
        if not patient_case:
            self.status_label.setText("请先加载或输入患者病例！")
            self.status_label.setStyleSheet("color: red;")
            return
        
        self.status_label.setText("正在整理病例，请稍候...")
        self.status_label.setStyleSheet("color: blue;")
        QApplication.processEvents()  # 立即更新界面
        
        # 调用整理功能
        success, result = organize_patient_case(patient_case)
        
        if success:
            # 将整理后的内容放回病例文本框，使用Markdown格式
            self.case_text_edit.setMarkdown(result)
            self.status_label.setText("病例整理成功！")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"病例整理失败：{result}")
            self.status_label.setStyleSheet("color: red;")
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreeningApp()
    ex.show()
    sys.exit(app.exec_())