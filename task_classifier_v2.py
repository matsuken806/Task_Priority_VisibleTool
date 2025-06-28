import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QStackedWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import pandas as pd

# メトリクス項目
METRICS = [
    '緊急度', '労力', '影響度', '必要なエネルギー', 'モチベーション', '自己犠牲感'
]
GENRES = ['仕事', '家事', 'リフレッシュ', '自己研鑽', '交際関係']

class TaskClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('タスク分類ツール')
        # デフォルトウィンドウサイズを設定
        self.resize(1200, 800)
        self.tasks = []  # 登録タスクリスト
        # テストタスクをあらかじめ5件登録, 内容はばらけるように一つ一つ登録しておく
        self.tasks = [
            {'タスク名': '仕事A', 'ジャンル': '仕事', '緊急度': 4, '労力': 3, '影響度': 5, '必要なエネルギー': 2, 'モチベーション': 4, '自己犠牲感': 1},
            {'タスク名': '家事B', 'ジャンル': '家事', '緊急度': 2, '労力': 4, '影響度': 3, '必要なエネルギー': 3, 'モチベーション': 2, '自己犠牲感': 2},
            {'タスク名': 'リフレッシュC', 'ジャンル': 'リフレッシュ', '緊急度': 1, '労力': 1, '影響度': 4, '必要なエネルギー': 5, 'モチベーション': 5, '自己犠牲感': 1},
            {'タスク名': '自己研鑽D', 'ジャンル': '自己研鑽', '緊急度': 3, '労力': 2, '影響度': 5, '必要なエネルギー': 4, 'モチベーション': 3, '自己犠牲感': 2},
            {'タスク名': '交際関係E', 'ジャンル': '交際関係', '緊急度': 5, '労力': 5, '影響度': 2, '必要なエネルギー': 1, 'モチベーション': 4, '自己犠牲感': 3}
        ]

        # スタックページ
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 各ページの作成
        self.menuPage = self.create_menu_page()
        self.registerPage = self.create_register_page()
        self.listPage = self.create_list_page()
        self.resultPage = self.create_result_page()
        for p in [self.menuPage, self.registerPage, self.listPage, self.resultPage]:
            self.stack.addWidget(p)
        self.show_menu()

    # 状態A: メニュー
    def create_menu_page(self):
        w = QWidget(); layout = QVBoxLayout(w)
        btn_reg = QPushButton('タスク登録'); btn_list = QPushButton('タスク一覧'); btn_res = QPushButton('結果表示')
        btn_reg.clicked.connect(self.show_register)
        btn_list.clicked.connect(self.show_list)
        btn_res.clicked.connect(self.show_results)
        for btn in (btn_reg, btn_list, btn_res): layout.addWidget(btn)
        return w

    # 状態B: タスク登録
    def create_register_page(self):
        w = QWidget(); layout = QVBoxLayout(w)
        # 入力フィールド
        self.input_name = QLineEdit()
        self.input_genre = QComboBox(); self.input_genre.addItems(GENRES)
        layout.addWidget(QLabel('タスク名')); layout.addWidget(self.input_name)
        layout.addWidget(QLabel('ジャンル')); layout.addWidget(self.input_genre)
        # 各評価 (0.5刻み)
        self.inputs_metric = {}
        for m in METRICS:
            sb = QDoubleSpinBox()
            sb.setRange(1.0, 5.0)
            sb.setSingleStep(0.5)
            sb.setValue(3.0)
            sb.setDecimals(1)
            self.inputs_metric[m] = sb
            hl = QHBoxLayout(); hl.addWidget(QLabel(m)); hl.addWidget(sb)
            layout.addLayout(hl)
        # ボタン
        btn_submit = QPushButton('登録'); btn_back = QPushButton('メニューへ戻る'); btn_list = QPushButton('一覧へ')
        btn_submit.clicked.connect(self.add_task)
        btn_back.clicked.connect(self.show_menu)
        btn_list.clicked.connect(self.show_list)
        hl_btn = QHBoxLayout(); hl_btn.addWidget(btn_submit); hl_btn.addWidget(btn_list); hl_btn.addWidget(btn_back)
        layout.addLayout(hl_btn)
        return w

    # 状態C: タスク一覧・編集
    def create_list_page(self):
        w = QWidget(); layout = QVBoxLayout(w)
        self.table = QTableWidget(0, 2+len(METRICS))
        headers = ['タスク名', 'ジャンル'] + METRICS
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)
        btn_edit = QPushButton('編集'); btn_back = QPushButton('メニューへ戻る')
        btn_edit.clicked.connect(self.edit_task)
        btn_back.clicked.connect(self.show_menu)
        hl = QHBoxLayout(); hl.addWidget(btn_edit); hl.addWidget(btn_back)
        layout.addLayout(hl)
        return w

    # 状態D: 結果表示
    def create_result_page(self):
        w = QWidget(); layout = QVBoxLayout(w)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.res_container = QWidget(); self.res_layout = QVBoxLayout(self.res_container)
        self.scroll.setWidget(self.res_container)
        layout.addWidget(self.scroll)
        btn_back = QPushButton('メニューへ戻る'); btn_back.clicked.connect(self.show_menu)
        layout.addWidget(btn_back)
        return w

    # ページ表示
    def show_menu(self): self.stack.setCurrentWidget(self.menuPage)
    def show_register(self):
        self.clear_form(); self.stack.setCurrentWidget(self.registerPage)
    def show_list(self):
        self.update_table(); self.stack.setCurrentWidget(self.listPage)
    def show_results(self):
        if not self.tasks:
            QMessageBox.warning(self, 'エラー', 'タスクが登録されていません')
            return
        self.display_results(); self.stack.setCurrentWidget(self.resultPage)

    # タスク追加
    def add_task(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, 'エラー', 'タスク名を入力してください')
            return
        data = {'タスク名': name, 'ジャンル': self.input_genre.currentText()}
        for m, sb in self.inputs_metric.items(): data[m] = sb.value()
        # 編集モード判定
        if hasattr(self, 'editing_index'):
            self.tasks[self.editing_index] = data
            del self.editing_index
        else:
            self.tasks.append(data)
        QMessageBox.information(self, '完了', 'タスクを登録しました')
        self.show_register()

    # 一覧更新
    def update_table(self):
        self.table.setRowCount(len(self.tasks))
        for i, t in enumerate(self.tasks):
            self.table.setItem(i, 0, QTableWidgetItem(t['タスク名']))
            self.table.setItem(i, 1, QTableWidgetItem(t['ジャンル']))
            for j, m in enumerate(METRICS, start=2):
                self.table.setItem(i, j, QTableWidgetItem(f"{t[m]:.1f}"))

    # 編集選択
    def edit_task(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'エラー', '編集するタスクを選択してください')
            return
        t = self.tasks[row]
        self.editing_index = row
        self.input_name.setText(t['タスク名'])
        self.input_genre.setCurrentText(t['ジャンル'])
        for m, sb in self.inputs_metric.items(): sb.setValue(t[m])
        self.stack.setCurrentWidget(self.registerPage)

    # フォーム初期化
    def clear_form(self):
        self.input_name.clear(); self.input_genre.setCurrentIndex(0)
        for sb in self.inputs_metric.values(): sb.setValue(3.0)
        if hasattr(self, 'editing_index'): del self.editing_index

    # 結果表示 (状態D)
    def display_results(self):
        for i in reversed(range(self.res_layout.count())):
            widget = self.res_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        df = pd.DataFrame(self.tasks)
        from itertools import combinations
        for x, y in combinations(METRICS, 2):
            fig = go.Figure(data=go.Scatter(
                x=df[x], y=df[y], mode='markers+text', text=df['タスク名'], textposition='top center'
            ))
            # X=3, Y=3の軸線を追加
            fig.add_shape(type='line', x0=0, y0=3, x1=6, y1=3,
                          line=dict(color='black', width=2))
            fig.add_shape(type='line', x0=3, y0=0, x1=3, y1=6,
                          line=dict(color='black', width=2))
            fig.update_layout(title=f'{x} vs {y}', xaxis_title=x, yaxis_title=y,
                             xaxis=dict(range=[0, 6]), yaxis=dict(range=[0, 6]))
            html = fig.to_html(include_plotlyjs='cdn', full_html=False)
            view = QWebEngineView(); view.setHtml(html)
            view.setMinimumHeight(600)
            self.res_layout.addWidget(view)
        df['総合評価'] = df[METRICS].sum(axis=1)
        df_sorted = df.sort_values('総合評価', ascending=False)
        fig2 = go.Figure(data=go.Bar(
            x=df_sorted['タスク名'], y=df_sorted['総合評価'], text=df_sorted['総合評価'], textposition='auto'
        ))
        fig2.update_layout(title='総合評価順位', xaxis_title='タスク', yaxis_title='総合評価')
    
        html2 = fig2.to_html(include_plotlyjs='cdn', full_html=False)
        view2 = QWebEngineView(); view2.setHtml(html2)
        view2.setMinimumHeight(600)
        self.res_layout.addWidget(view2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskClassifierApp()
    window.show()
    sys.exit(app.exec_())
