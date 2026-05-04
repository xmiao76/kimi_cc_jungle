import pytest
from PyQt6.QtCore import Qt
from jungle.model.pieces import Side
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

    def test_play_as_red(self, window):
        window.side_combo.setCurrentIndex(1)  # Red
        assert window.controller.human_side is Side.RED
        assert window.board_widget._flipped

    def test_play_as_red_ai_moves_first(self, window, qtbot):
        window.side_combo.setCurrentIndex(1)  # Red
        qtbot.mouseClick(window.new_game_btn, Qt.MouseButton.LeftButton)
        assert "BLUE" in window.turn_label.text()
        # Blue is AI, so _check_ai_turn should schedule AI
        assert window.controller._ai_thinking or "thinking" in window.status_label.text().lower()

    def test_side_combo_hidden_in_hotseat(self, window):
        window.mode_combo.setCurrentIndex(1)  # Hotseat
        assert not window.side_combo.isVisible()

    def test_difficulty_combo_hidden_in_hotseat(self, window):
        window.mode_combo.setCurrentIndex(1)  # Hotseat
        assert not window.difficulty_combo.isVisible()

    def test_difficulty_updates_slider(self, window):
        window.difficulty_combo.setCurrentIndex(3)  # Expert
        assert window.speed_slider.value() == 5000
        window.difficulty_combo.setCurrentIndex(0)  # Beginner
        assert window.speed_slider.value() == 200
        assert window.controller._ai_think_time_ms == 200

    def test_difficulty_visible_in_ai_vs_ai(self, window):
        window.mode_combo.setCurrentIndex(2)  # AI vs AI
        assert window.difficulty_combo.isVisible()
