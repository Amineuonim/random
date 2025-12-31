#!/usr/bin/env python3
"""
turing_simulator.py

PyQt5 Turing Machine simulator for TP 03.

Features:
- Enter machine definition: states, alphabet (including blank symbol), start state, final states
- Enter transition rules in text format (see README inside the GUI)
- Initialize tape with input string
- Step-by-step simulation, or run automatically
- Display tape at each step with head highlighted, current state, step counter, and logs

Author: ChatGPT (assistant)
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets

# ---------- Core Turing Machine Logic ----------

def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


class TuringMachine:
    def __init__(self, states=None, alphabet=None, blank='_', start_state=None, final_states=None, transitions=None):
        self.states = set(states or [])
        self.alphabet = set(alphabet or [])
        self.blank = blank
        self.start_state = start_state
        self.final_states = set(final_states or [])
        self.transitions = transitions or {}  # dict: (state, symbol) -> (new_state, write_symbol, move)
        self.reset()

    def reset(self):
        # Tape is a dict mapping integer positions to symbols
        self.tape = {}
        self.head = 0
        self.current_state = self.start_state
        self.step_count = 0
        self.halted = False
        self.accepted = False

    def load_tape_from_string(self, s):
        self.tape = {i: ch for i, ch in enumerate(s)}
        if not self.tape:
            # empty tape -> ensure at least blank at position 0
            self.tape = {0: self.blank}
        self.head = 0

    def read(self):
        return self.tape.get(self.head, self.blank)

    def write(self, symbol):
        if symbol == self.blank:
            # optional clean-up: remove blank to keep tape sparse
            if self.head in self.tape:
                self.tape.pop(self.head, None)
        else:
            self.tape[self.head] = symbol

    def step(self):
        if self.halted:
            return None  # already halted

        read_symbol = self.read()
        key = (self.current_state, read_symbol)
        if key not in self.transitions:
            # no rule -> halt
            self.halted = True
            self.accepted = (self.current_state in self.final_states)
            return {
                'action': 'halt',
                'reason': 'no_transition',
                'state': self.current_state,
                'read': read_symbol
            }

        new_state, write_symbol, move = self.transitions[key]
        # apply
        self.write(write_symbol)
        if move.upper() == 'R':
            self.head += 1
        elif move.upper() == 'L':
            self.head -= 1
        elif move.upper() == 'S' or move.upper() == 'N':
            pass  # stay
        else:
            # unknown move -- treat as stay
            pass

        self.current_state = new_state
        self.step_count += 1

        if self.current_state in self.final_states:
            self.halted = True
            self.accepted = True
            return {
                'action': 'accept',
                'state': self.current_state
            }

        return {
            'action': 'transition',
            'new_state': new_state,
            'write': write_symbol,
            'move': move,
            'head': self.head,
            'step': self.step_count
        }

    def get_tape_snapshot(self, left=-20, right=20):
        # returns list of symbols for positions [left..right]
        # automatically expand to include occupied cells
        if self.tape:
            min_k = min(self.tape.keys())
            max_k = max(self.tape.keys())
            left = min(left, min_k - 5)
            right = max(right, max_k + 5)
        return [self.tape.get(i, self.blank) for i in range(left, right + 1)], left

# ---------- GUI ----------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Turing Machine Simulator (TP 03)")
        self.resize(1000, 700)
        self._tm = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._auto_step)
        self._setup_ui()
        self._load_example()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Top: machine definition
        top_layout = QtWidgets.QHBoxLayout()
        left_col = QtWidgets.QFormLayout()
        self.states_edit = QtWidgets.QLineEdit()
        self.alphabet_edit = QtWidgets.QLineEdit()
        self.blank_edit = QtWidgets.QLineEdit('_')
        self.start_state_edit = QtWidgets.QLineEdit()
        self.final_states_edit = QtWidgets.QLineEdit()
        left_col.addRow("States (comma):", self.states_edit)
        left_col.addRow("Alphabet (comma):", self.alphabet_edit)
        left_col.addRow("Blank symbol:", self.blank_edit)
        left_col.addRow("Start state:", self.start_state_edit)
        left_col.addRow("Final states (comma):", self.final_states_edit)

        top_layout.addLayout(left_col, 1)

        # Transition rules
        rules_layout = QtWidgets.QVBoxLayout()
        rules_layout.addWidget(QtWidgets.QLabel("Transition rules (one per line):"))
        self.rules_text = QtWidgets.QPlainTextEdit()
        rules_layout.addWidget(self.rules_text)
        rules_help = QtWidgets.QLabel(
            "Format: current_state,read_symbol -> new_state,write_symbol,move\n"
            "Example: q0,1 -> q1,1,R\n"
            "move: L (left), R (right), S (stay)\n"
            "Blank symbol example: _"
        )
        rules_help.setWordWrap(True)
        rules_layout.addWidget(rules_help)
        top_layout.addLayout(rules_layout, 2)

        layout.addLayout(top_layout)

        # Tape & controls
        mid_layout = QtWidgets.QHBoxLayout()

        tape_group = QtWidgets.QGroupBox("Tape & Visualization")
        tape_vlayout = QtWidgets.QVBoxLayout()
        self.tape_display = QtWidgets.QLabel()
        self.tape_display.setAlignment(QtCore.Qt.AlignCenter)
        self.tape_display.setMinimumHeight(80)
        self.tape_display.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.tape_display.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        tape_vlayout.addWidget(self.tape_display)

        info_h = QtWidgets.QHBoxLayout()
        self.state_label = QtWidgets.QLabel("State: -")
        self.step_label = QtWidgets.QLabel("Step: 0")
        info_h.addWidget(self.state_label)
        info_h.addStretch(1)
        info_h.addWidget(self.step_label)
        tape_vlayout.addLayout(info_h)

        tape_group.setLayout(tape_vlayout)
        mid_layout.addWidget(tape_group, 2)

        controls_group = QtWidgets.QGroupBox("Controls")
        controls_v = QtWidgets.QVBoxLayout()

        form = QtWidgets.QFormLayout()
        self.tape_input = QtWidgets.QLineEdit()
        self.tape_input.setPlaceholderText("Initial tape contents, e.g. 1101")
        form.addRow("Initial tape:", self.tape_input)
        controls_v.addLayout(form)

        btn_h = QtWidgets.QHBoxLayout()
        self.load_example_btn = QtWidgets.QPushButton("Load Example")
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.step_btn = QtWidgets.QPushButton("Step")
        self.run_btn = QtWidgets.QPushButton("Run")
        btn_h.addWidget(self.load_example_btn)
        btn_h.addWidget(self.reset_btn)
        btn_h.addWidget(self.step_btn)
        btn_h.addWidget(self.run_btn)
        controls_v.addLayout(btn_h)

        speed_layout = QtWidgets.QHBoxLayout()
        speed_layout.addWidget(QtWidgets.QLabel("Speed (ms per step):"))
        self.speed_spin = QtWidgets.QSpinBox()
        self.speed_spin.setRange(50, 5000)
        self.speed_spin.setValue(400)
        speed_layout.addWidget(self.speed_spin)
        controls_v.addLayout(speed_layout)

        self.clear_log_btn = QtWidgets.QPushButton("Clear Log")
        controls_v.addWidget(self.clear_log_btn)

        controls_group.setLayout(controls_v)
        mid_layout.addWidget(controls_group, 1)

        layout.addLayout(mid_layout)

        # Log
        log_group = QtWidgets.QGroupBox("Execution Log")
        log_v = QtWidgets.QVBoxLayout()
        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)
        log_v.addWidget(self.log_view)
        log_group.setLayout(log_v)
        layout.addWidget(log_group, 1)

        # Connections
        self.load_example_btn.clicked.connect(self._load_example)
        self.reset_btn.clicked.connect(self._reset_machine)
        self.step_btn.clicked.connect(self._step)
        self.run_btn.clicked.connect(self._toggle_run)
        self.clear_log_btn.clicked.connect(lambda: self.log_view.clear())

        # keyboard shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, activated=self._step)
        QtWidgets.QShortcut(QtGui.QKeySequence("R"), self, activated=self._toggle_run)

    # ---------- Parsing & loading ----------

    def _parse_transitions(self, text, blank_symbol):
        """
        Parse lines of transition rules. Return dict: (state, read) -> (new_state, write, move)
        Accepts formats like:
          q0,1 -> q1,1,R
          q0, _ -> q_accept, _, S
        """
        transitions = {}
        lines = text.splitlines()
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            # normalize arrows
            if '->' not in line:
                # try alternative
                parts = line.split()
                if len(parts) >= 3 and parts[1] == '->':
                    left = parts[0]
                    right = ' '.join(parts[2:])
                else:
                    # invalid line
                    continue
            else:
                left, right = line.split('->', 1)
            left = left.strip()
            right = right.strip()
            # left: state,symbol
            if ',' not in left:
                continue
            cur_state, read_sym = [p.strip() for p in left.split(',', 1)]
            # right: new_state,write,move
            right_parts = [p.strip() for p in right.split(',')]
            if len(right_parts) < 3:
                # if move missing, assume S
                if len(right_parts) == 2:
                    new_state, write_symbol = right_parts
                    move = 'S'
                else:
                    continue
            else:
                new_state, write_symbol, move = right_parts[:3]
            # convert empty symbols to blank symbol
            if read_sym == '':
                read_sym = blank_symbol
            if write_symbol == '':
                write_symbol = blank_symbol
            transitions[(cur_state, read_sym)] = (new_state, write_symbol, move.upper())
        return transitions

    def _create_machine_from_ui(self):
        states = [s.strip() for s in self.states_edit.text().split(',') if s.strip()]
        alphabet = [s.strip() for s in self.alphabet_edit.text().split(',') if s.strip()]
        blank = self.blank_edit.text() or '_'
        start = self.start_state_edit.text().strip()
        finals = [s.strip() for s in self.final_states_edit.text().split(',') if s.strip()]
        transitions = self._parse_transitions(self.rules_text.toPlainText(), blank)
        tm = TuringMachine(states=states, alphabet=alphabet, blank=blank,
                           start_state=start, final_states=finals, transitions=transitions)
        return tm

    def _load_example(self):
        # Prefill UI with a simple example: recognize strings with an even number of 1's
        self.states_edit.setText("q0,q1,q_accept,q_reject")
        self.alphabet_edit.setText("1,0,_")
        self.blank_edit.setText("_")
        self.start_state_edit.setText("q0")
        self.final_states_edit.setText("q_accept")
        example_rules = "\n".join([
            "# Example: accept strings with an even number of '1' (binary alphabet)",
            "q0,1 -> q1,1,R",
            "q1,1 -> q0,1,R",
            "q0,0 -> q0,0,R",
            "q1,0 -> q1,0,R",
            "q0,_ -> q_accept,_,S",
            "q1,_ -> q_reject,_,S"
        ])
        self.rules_text.setPlainText(example_rules)
        self.tape_input.setText("1101")  # example tape
        self.log_view.clear()
        self._reset_machine()

    def _reset_machine(self):
        self.timer.stop()
        self.run_btn.setText("Run")
        try:
            tm = self._create_machine_from_ui()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Parsing error", f"Could not create machine: {e}")
            return
        self._tm = tm
        self._tm.reset()
        self._tm.load_tape_from_string(self.tape_input.text())
        self._update_display()
        self.log_view.appendPlainText("Machine loaded and reset.")
        self._log_machine_summary()

    def _log_machine_summary(self):
        if not self._tm:
            return
        self.log_view.appendPlainText(f"Start state: {self._tm.start_state}")
        self.log_view.appendPlainText(f"Final states: {', '.join(sorted(self._tm.final_states))}")
        self.log_view.appendPlainText(f"Blank symbol: '{self._tm.blank}'")
        self.log_view.appendPlainText(f"Transitions loaded: {len(self._tm.transitions)}")

    # ---------- Visualization & stepping ----------

    def _format_tape_html(self, window=25):
        if not self._tm:
            return ""
        tape_list, left_idx = self._tm.get_tape_snapshot(left=-window, right=window)
        # determine the index in the snapshot corresponding to head
        head_pos = self._tm.head
        head_index = head_pos - left_idx
        # Build HTML where head position is highlighted
        cells = []
        for i, sym in enumerate(tape_list):
            pos = left_idx + i
            if i == head_index:
                # highlight head
                cells.append(f"<span style='background:#ffd54f; padding:4px 6px; border-radius:4px; "
                             f"display:inline-block; min-width:18px; text-align:center; font-weight:bold;'>{html_escape(sym)}</span>")
            else:
                cells.append(f"<span style='padding:4px 6px; display:inline-block; min-width:18px; text-align:center;'>{html_escape(sym)}</span>")
        # show positions below
        positions = []
        for i, _ in enumerate(tape_list):
            pos = left_idx + i
            if i == head_index:
                positions.append(f"<span style='display:inline-block; min-width:18px; text-align:center; font-size:80%; color:#555;'>[{pos}]</span>")
            else:
                positions.append(f"<span style='display:inline-block; min-width:18px; text-align:center; font-size:80%; color:#888;'>{pos}</span>")
        tape_html = "<div style='font-family:monospace;'>" + " ".join(cells) + "<br>" + " ".join(positions) + "</div>"
        return tape_html

    def _update_display(self):
        if not self._tm:
            self.tape_display.setText("No machine loaded")
            self.state_label.setText("State: -")
            self.step_label.setText("Step: 0")
            return
        html = self._format_tape_html(window=20)
        self.tape_display.setText(html)
        self.tape_display.setTextFormat(QtCore.Qt.RichText)
        self.state_label.setText(f"State: {self._tm.current_state}")
        self.step_label.setText(f"Step: {self._tm.step_count}")

    def _step(self):
        if not self._tm:
            self._reset_machine()
            return
        if self._tm.halted:
            self.log_view.appendPlainText("Machine already halted. Reset to run again.")
            return
        result = self._tm.step()
        if result is None:
            return
        if result['action'] == 'transition':
            self.log_view.appendPlainText(f"Step {self._tm.step_count}: moved {result['move']}, wrote '{result['write']}', new state '{result['new_state']}'. Head at {self._tm.head}")
        elif result['action'] == 'accept':
            self.log_view.appendPlainText(f"Machine accepted in state '{result['state']}' after {self._tm.step_count} steps.")
        elif result['action'] == 'halt':
            accepted = "ACCEPT" if self._tm.current_state in self._tm.final_states else "REJECT"
            self.log_view.appendPlainText(f"Machine halted (no transition). State: '{result['state']}'. {accepted} after {self._tm.step_count} steps.")
        else:
            self.log_view.appendPlainText(str(result))
        self._update_display()

    def _toggle_run(self):
        if not self._tm:
            self._reset_machine()
            return
        if self.timer.isActive():
            self.timer.stop()
            self.run_btn.setText("Run")
            self.log_view.appendPlainText("Run paused.")
        else:
            interval = int(self.speed_spin.value())
            self.timer.start(interval)
            self.run_btn.setText("Pause")
            self.log_view.appendPlainText("Running... (press Run/ Pause or 'R' to toggle)")

    def _auto_step(self):
        if not self._tm or self._tm.halted:
            if self.timer.isActive():
                self.timer.stop()
                self.run_btn.setText("Run")
            return
        self._step()

# ---------- Utility for HTML escaping (PyQt5 lacks direct simple helper) ----------

# Add helper to escape small HTML content

# ---------- Run ----------

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
