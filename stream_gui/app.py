import sys
import os
from PyQt6.QtCore import QProcess, QByteArray
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QApplication
# from PyQt6 import uic

from .stream_execute import Ui_MainWindow

# Get the directory path of the current module file
module_dir = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        
        # uic.loadUi(os.path.join(module_dir, "../ui/stream_execute.ui"), self)

        #
        self.p = None

        # Connect
        self.inputFile_PB.clicked.connect(self.show_input_file_dialog)
        self.outputDirectory_PB.clicked.connect(self.show_output_directory_dialog)
        self.launchSimulation_PB.clicked.connect(self.launch_simulation)
        self.stopSimulation_PB.clicked.connect(self.stop_simulation)

    def show_input_file_dialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileUrl(parent = self, caption="Select an input file", filter="Numpy Data Files (*.npy)")

        if file_path:
            self.inputFile_LE.setText(file_path.toLocalFile())

    def show_output_directory_dialog(self):
        file_dialog = QFileDialog()
        selected_directory = file_dialog.getExistingDirectoryUrl(parent = self, caption="Select an input file")

        if selected_directory:
            self.outputDirectory_LE.setText(selected_directory.toLocalFile())
    
    def message(self, s):
        self.logSimulation_TE.appendPlainText(s)
    
    def launch_simulation(self):
        if self.p is None:
            input_file = self.inputFile_LE.text()
            output_dir = self.outputDirectory_LE.text()

            self.p = QProcess()
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.simulation_finished)
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.start("python", ["-m", "stream", "-i" ,input_file, "-o", output_dir, '--display_advance' ])
    
    def stop_simulation(self):
        self.p.kill()
        self.p.waitForFinished()

    def handle_stdout(self):
        data = QByteArray()
        while self.p.canReadLine():
            data += self.p.readLine()
        stdout = data.data().decode()
        splitted = stdout.split(',')
        if splitted[0] == 'simulation':
            self.simulation_progress.setValue(float(splitted[1]))
            self.task_Label.setText('simulation')
        else:
            self.message(stdout)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"Simulation state changed: {state_name}")

        if state == QProcess.ProcessState.NotRunning:
            self.stopSimulation_PB.setEnabled(False)
            self.launchSimulation_PB.setEnabled(True)
            self.simulation_progress.setEnabled(False)
        else:
            self.stopSimulation_PB.setEnabled(True)
            self.launchSimulation_PB.setEnabled(False)
            self.simulation_progress.setEnabled(True)

    
    def simulation_finished(self):
        self.p = None

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()