import time

import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QPoint
import json

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class Worker(QtCore.QObject):
    def __init__(self, snip_window, image_lang_code, trans_lang_code, is_text2speech_enabled, ui, translator_engine,
                 img_lang, trans_lang):
        super().__init__()
        self.x1 = min(snip_window.begin.x(), snip_window.end.x())
        self.y1 = min(snip_window.begin.y(), snip_window.end.y())
        self.x2 = max(snip_window.begin.x(), snip_window.end.x())
        self.y2 = max(snip_window.begin.y(), snip_window.end.y())
        self.image_lang_code = image_lang_code
        self.trans_lang_code = trans_lang_code
        self.is_text2speech_enabled = is_text2speech_enabled
        self.ui = ui
        self.running = True
        self.translator_engine = translator_engine
        self.current_extracted_text = None
        self.last_extracted_text = None
        self.img_lang = img_lang.lower()
        self.trans_lang = trans_lang.lower()

    def stop_running(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                img = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
                img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
            except Exception:
                time.sleep(0.5)
                continue

            new_extracted_text = pytesseract.image_to_string(img, lang=self.image_lang_code).strip()
            new_extracted_text = " ".join(new_extracted_text.split())
            print(f"EXTRACTED TEXT: [{new_extracted_text}]")

            if len(new_extracted_text) < 6 or len(new_extracted_text) > 4999:
                time.sleep(0.3)
                continue

            words = new_extracted_text.split()
            if len(words) < 3 or (sum(len(w) for w in words) * 1.0 / len(words)) <= 2:
                time.sleep(0.3)
                continue

            if self.last_extracted_text != new_extracted_text:
                self.last_extracted_text = new_extracted_text
                time.sleep(0.2)
                continue

            if self.current_extracted_text != new_extracted_text and new_extracted_text:
                self.ui.set_title('Translating')
                print(f"Translating: [{new_extracted_text}] of len[{len(new_extracted_text)}]")
                self.current_extracted_text = new_extracted_text

                translated_text = ""
                print(self.img_lang, self.trans_lang)
                if self.translator_engine == "OllamaTranslator":
                    try:
                        from . import ollama_translate
                        set_pending = lambda x: self.ui.set_text(x)
                        translated_text = ollama_translate.translate(new_extracted_text, set_pending=set_pending)
                        print(f"TRANSLATED TEXT: [{translated_text}]")
                    except Exception:
                        print("unsupported by OllamaTranslator")
                elif self.translator_engine == "GoogleTranslator":
                    try:
                        from deep_translator import GoogleTranslator
                        translated_text = GoogleTranslator(source='auto', target=self.trans_lang_code).translate(
                            new_extracted_text)
                        print(f"TRANSLATED TEXT: [{translated_text}]")
                    except Exception:
                        print("unsupported by GoogleTranslate")
                elif self.translator_engine == "PonsTranslator":
                    try:
                        from deep_translator import PonsTranslator
                        translated_text = PonsTranslator(source=self.img_lang, target=self.trans_lang).translate(
                            new_extracted_text)
                        print(f"TRANSLATED TEXT: [{translated_text}]")
                    except Exception:
                        print("unsupported by PonsTranslator")
                elif self.translator_engine == "LingueeTranslator":
                    try:
                        from deep_translator import LingueeTranslator
                        translated_text = LingueeTranslator(source=self.img_lang, target=self.trans_lang).translate(
                            new_extracted_text)
                        print(f"TRANSLATED TEXT: [{translated_text}]")
                    except Exception:
                        print("unsupported by LingueeTranslator")
                else:
                    try:
                        from deep_translator import MyMemoryTranslator
                        translated_text = MyMemoryTranslator(source=self.img_lang, target=self.trans_lang).translate(
                            new_extracted_text)
                        print(f"TRANSLATED TEXT: [{translated_text}]")
                    except Exception:
                        print("unsupported by MyMemoryTranslator")

                self.ui.set_text(translated_text)
                if self.is_text2speech_enabled:
                    import pyttsx3

                    engine = pyttsx3.init()
                    engine.say(translated_text)
                    engine.runAndWait()

            self.ui.set_title('')

            time.sleep(0.2)


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.availableGeometry()
        screen_width = rect.width()
        screen_height = rect.height()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.show()
        self.is_empty_selection = True
        self.load_config()

    def save_config(self):
        with open('snap-config.json', 'w') as f:
            json.dump([self.begin.x(), self.begin.y(), self.end.x(), self.end.y()], f)

    def load_config(self):
        try:
            with open('snap-config.json', 'r') as f:
                data = json.load(f)
                self.begin = QPoint(data[0], data[1])
                self.end   = QPoint(data[2], data[3])
            self.is_empty_selection = False
        except Exception:
            pass

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        self.save_config()
        self.is_empty_selection = False

    def closeEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor)
        )


if __name__ == '__main__':
    app = QtWidgets.QApplication([""])
    window = MyWidget()
    QtWidgets.QApplication.setOverrideCursor(
        QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor)
    )
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    app.exec_()
