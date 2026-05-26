# -*- coding: utf-8 -*-

import wx

import addonHandler
import api
import globalPluginHandler
import gui
import ui
from scriptHandler import script

addonHandler.initTranslation()

try:
    _
except NameError:
    _ = lambda text: text

from . import currency
from . import storage
from .dialogs import ConverterFrame, ask_amount


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Currency converter")

    def __init__(self):
        super().__init__()
        self.frame = None
        self.menu_item = None

        try:
            self.menu_item = gui.mainFrame.sysTrayIcon.toolsMenu.Append(
                wx.ID_ANY,
                _("&Currency converter...")
            )
            gui.mainFrame.sysTrayIcon.Bind(
                wx.EVT_MENU,
                self.on_menu,
                self.menu_item
            )
        except Exception:
            self.menu_item = None

    def terminate(self):
        try:
            if self.frame:
                self.frame.Destroy()
                self.frame = None
        except Exception:
            pass

        try:
            if self.menu_item:
                gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self.menu_item)
                self.menu_item = None
        except Exception:
            pass

    def on_menu(self, event):
        self.open_main_window()

    def on_frame_closed(self):
        self.frame = None

    def open_main_window(self):
        if self.frame:
            try:
                self.frame.Raise()
                self.frame.SetFocus()
                return
            except Exception:
                self.frame = None

        self.frame = ConverterFrame(gui.mainFrame, on_close=self.on_frame_closed)
        self.frame.Show()
        self.frame.Raise()

    def refresh_frame(self):
        if self.frame:
            self.frame.data = storage.load_data()
            self.frame.amount.SetValue(str(self.frame.data.get("last_amount", "1")))
            self.frame.source.SetSelection(
                self.frame.index_for_code(self.frame.data.get("last_source", "EUR"))
            )
            self.frame.target.SetSelection(
                self.frame.index_for_code(self.frame.data.get("last_target", "USD"))
            )
            self.frame.refresh_history()

    def copy_text_to_clipboard(self, text):
        try:
            api.copyToClip(text)
            return True
        except Exception:
            pass

        try:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()
                return True
        except Exception:
            try:
                wx.TheClipboard.Close()
            except Exception:
                pass

        return False

    def convert_with_amount_dialog(self):
        data = storage.load_data()
        amount_text = ask_amount(gui.mainFrame, data.get("last_amount", "1"))

        if amount_text is None:
            return

        amount = currency.parse_amount(amount_text)
        source = data.get("last_source", "EUR")
        target = data.get("last_target", "USD")
        result = currency.convert(amount, source, target)
        message = currency.result_message(result)

        data["last_amount"] = amount_text
        data["last_source"] = source
        data["last_target"] = target
        storage.add_history_item(message)
        storage.save_data(data)

        self.refresh_frame()
        copied = self.copy_text_to_clipboard(message)

        if copied:
            ui.message(_("{result} Result copied to clipboard.").format(result=message))
        else:
            ui.message(message)

    def speak_last_result(self):
        ui.message(storage.get_last_result_message())

    def swap_last_currencies(self):
        data = storage.load_data()
        source = data.get("last_source", "EUR")
        target = data.get("last_target", "USD")
        data["last_source"] = target
        data["last_target"] = source
        storage.save_data(data)

        if self.frame:
            wx.CallAfter(self.refresh_frame)

        ui.message(_("Currencies swapped. From {source} to {target}.").format(
            source=target,
            target=source
        ))

    @script(
        description=_("Open the currency converter window"),
        category=_("Currency converter")
    )
    def script_openMainWindow(self, gesture):
        wx.CallAfter(self.open_main_window)

    @script(
        description=_("Enter an amount and convert using the last saved currencies"),
        category=_("Currency converter")
    )
    def script_convertLast(self, gesture):
        wx.CallAfter(self._script_convert_with_dialog)

    def _script_convert_with_dialog(self):
        try:
            self.convert_with_amount_dialog()
        except Exception as e:
            ui.message(str(e))

    @script(
        description=_("Speak the last currency conversion result"),
        category=_("Currency converter")
    )
    def script_speakLastResult(self, gesture):
        self.speak_last_result()

    @script(
        description=_("Swap the last currencies used by the currency converter"),
        category=_("Currency converter")
    )
    def script_swapLastCurrencies(self, gesture):
        self.swap_last_currencies()
