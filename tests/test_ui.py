import pytest
from PyQt6.QtCore import Qt
from jungle.ui.main_window import MainWindow

@pytest.fixture
def window(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    return w

class TestMainWindow:
    def test_window_title(self, window):
        assert window.windowTitle() == "Jungle / Dou Shou Qi"

    def test_board_visible(self, window):
        assert window.board_widget.isVisible()
        assert window.board_widget.width() > 0
        assert window.board_widget.height() > 0

    def test_new_game_button(self, window, qtbot):
        qtbot.mouseClick(window.new_game_btn, Qt.MouseButton.LeftButton)
        assert not window.controller.state.is_game_over()

    def test_flip_board(self, window, qtbot):
        assert not window.board_widget._flipped
        qtbot.mouseClick(window.flip_btn, Qt.MouseButton.LeftButton)
        assert window.board_widget._flipped
        qtbot.mouseClick(window.flip_btn, Qt.MouseButton.LeftButton)
        assert not window.board_widget._flipped

    def test_initial_turn_label(self, window):
        assert "BLUE" in window.turn_label.text()

    def test_ai_vs_ai_mode(self, window, qtbot):
        window.mode_combo.setCurrentIndex(2)  # AI vs AI
        assert window.controller._ai_vs_ai
