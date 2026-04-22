from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QSlider
)

from jungle.model.pieces import Side
from .board_widget import BoardWidget
from .game_controller import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jungle / Dou Shou Qi")
        self.setMinimumSize(520, 700)

        self.controller = GameController(self)
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.turn_changed.connect(self._on_turn_changed)
        self.controller.game_over.connect(self._on_game_over)
        self.controller.message.connect(self._on_message)

        self._build_ui()
        self.controller.new_game()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        self.new_game_btn.clicked.connect(self.controller.new_game)
        top_layout.addWidget(self.new_game_btn)

        self.flip_btn = QPushButton("Flip Board")
        self.flip_btn.setCheckable(True)
        self.flip_btn.setStyleSheet("padding: 6px 12px;")
        self.flip_btn.toggled.connect(self._on_flip_toggled)
        top_layout.addWidget(self.flip_btn)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("vs AI", "vs_ai")
        self.mode_combo.addItem("Hotseat (2P)", "hotseat")
        self.mode_combo.addItem("AI vs AI", "ai_vs_ai")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        top_layout.addWidget(self.mode_combo)

        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Turn indicator
        self.turn_label = QLabel("Turn: Blue")
        self.turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 8px; "
            "background-color: #f0f0f0; border-radius: 6px;"
        )
        layout.addWidget(self.turn_label)

        # Board
        self.board_widget = BoardWidget()
        self.board_widget.square_clicked.connect(self.controller.handle_square_click)
        layout.addWidget(self.board_widget, stretch=1)

        # Status bar
        self.status_label = QLabel("Welcome to Jungle / Dou Shou Qi!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 13px; padding: 8px; color: #333; background-color: #fafafa; border-radius: 4px;"
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # AI speed control for AI-vs-AI
        self.speed_layout = QHBoxLayout()
        self.speed_label = QLabel("AI Delay:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(2000)
        self.speed_slider.setValue(300)
        self.speed_slider.setTickInterval(100)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.speed_value = QLabel("300 ms")
        self.speed_layout.addWidget(self.speed_label)
        self.speed_layout.addWidget(self.speed_slider)
        self.speed_layout.addWidget(self.speed_value)
        layout.addLayout(self.speed_layout)

        # Menu
        menubar = self.menuBar()
        game_menu = menubar.addMenu("Game")
        new_act = QAction("New Game", self)
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self.controller.new_game)
        game_menu.addAction(new_act)

        ai_vs_ai_act = QAction("AI vs AI", self)
        ai_vs_ai_act.setShortcut("Ctrl+W")
        ai_vs_ai_act.triggered.connect(self._start_ai_vs_ai)
        game_menu.addAction(ai_vs_ai_act)

        exit_act = QAction("Exit", self)
        exit_act.setShortcut("Alt+F4")
        exit_act.triggered.connect(self.close)
        game_menu.addAction(exit_act)

    def _on_state_changed(self):
        self.board_widget.set_game_state(self.controller.state)
        sel = self.controller.get_selected()
        self.board_widget.set_selected(*sel if sel else (None, None))

    def _on_turn_changed(self, side: Side):
        self.turn_label.setText(f"Turn: {side.name}")
        if side is Side.BLUE:
            self.turn_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; padding: 8px; "
                "background-color: #1E90FF; color: white; border-radius: 6px;"
            )
        else:
            self.turn_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; padding: 8px; "
                "background-color: #DC143C; color: white; border-radius: 6px;"
            )

    def _on_game_over(self, winner: Side):
        QMessageBox.information(self, "Game Over", f"{winner.name} wins the game!")

    def _on_message(self, msg: str):
        self.status_label.setText(msg)

    def _on_flip_toggled(self, checked: bool):
        self.board_widget.set_flipped(checked)

    def _on_mode_changed(self, index: int):
        mode = self.mode_combo.itemData(index)
        if mode == "vs_ai":
            self.controller.set_ai_vs_ai(False)
            self.controller.set_ai_enabled(True)
            self.controller.new_game()
        elif mode == "hotseat":
            self.controller.set_ai_vs_ai(False)
            self.controller.set_ai_enabled(False)
            self.controller.new_game()
        elif mode == "ai_vs_ai":
            self.controller.set_ai_vs_ai(True)
            self.controller.new_game()

    def _start_ai_vs_ai(self):
        self.mode_combo.setCurrentIndex(2)
        self.controller.set_ai_vs_ai(True)
        self.controller.new_game()

    def _on_speed_changed(self, value: int):
        self.controller.set_ai_delay(value)
        self.speed_value.setText(f"{value} ms")
