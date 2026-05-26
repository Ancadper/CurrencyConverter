# -*- coding: utf-8 -*-

import wx

import ui

from . import currency
from . import storage


try:
    _
except NameError:
    _ = lambda text: text

ADDON_NAME = _("Currency converter")


def info(parent, message):
    wx.MessageBox(message, ADDON_NAME, wx.OK | wx.ICON_INFORMATION, parent)


def error(parent, message):
    wx.MessageBox(message, ADDON_NAME, wx.OK | wx.ICON_ERROR, parent)


def ask_amount(parent, default_value="1"):
    dialog = wx.TextEntryDialog(
        parent,
        _("Enter the amount to convert:"),
        _("Convert currencies"),
        str(default_value),
    )

    try:
        if dialog.ShowModal() != wx.ID_OK:
            return None

        return dialog.GetValue()
    finally:
        dialog.Destroy()


class ConverterFrame(wx.Frame):
    def __init__(self, parent, on_close=None):
        super().__init__(
            parent,
            title=_("Currency converter"),
            size=(680, 430),
        )
        self.on_close_callback = on_close
        self.data = storage.load_data()
        self.create_menu()
        self.create_ui()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.CentreOnScreen()
        self.amount.SetFocus()

    def create_menu(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        convert_item = file_menu.Append(wx.ID_ANY, _("Convert"))
        swap_item = file_menu.Append(wx.ID_ANY, _("Swap currencies"))
        read_item = file_menu.Append(wx.ID_ANY, _("Speak last result"))
        file_menu.AppendSeparator()
        close_item = file_menu.Append(wx.ID_EXIT, _("Close\tAlt+F4"))

        help_menu = wx.Menu()
        privacy_item = help_menu.Append(wx.ID_ANY, _("Privacy"))
        about_item = help_menu.Append(wx.ID_ABOUT, _("About"))

        menu_bar.Append(file_menu, _("File"))
        menu_bar.Append(help_menu, _("Help"))
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_convert, convert_item)
        self.Bind(wx.EVT_MENU, self.on_swap, swap_item)
        self.Bind(wx.EVT_MENU, self.on_read_result, read_item)
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), close_item)
        self.Bind(wx.EVT_MENU, self.on_privacy, privacy_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def create_ui(self):
        panel = wx.Panel(self)
        main = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        grid.AddGrowableCol(1, 1)

        grid.Add(wx.StaticText(panel, label=_("Amount:")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.amount = wx.TextCtrl(panel, value=str(self.data.get("last_amount", "1")))
        grid.Add(self.amount, 1, wx.EXPAND)

        choices = currency.currency_choices()
        source_default = self.index_for_code(self.data.get("last_source", "EUR"))
        target_default = self.index_for_code(self.data.get("last_target", "USD"))

        grid.Add(wx.StaticText(panel, label=_("From:")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.source = wx.Choice(panel, choices=choices)
        self.source.SetSelection(source_default)
        grid.Add(self.source, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label=_("To:")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.target = wx.Choice(panel, choices=choices)
        self.target.SetSelection(target_default)
        grid.Add(self.target, 1, wx.EXPAND)

        main.Add(grid, 0, wx.EXPAND | wx.ALL, 12)

        main.Add(
            wx.StaticText(panel, label=_("Recent conversions:")),
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM,
            12,
        )

        self.history = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
        )
        self.history.AppendColumn(_("Result"), width=640)
        main.Add(self.history, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        convert_button = wx.Button(panel, label=_("Convert"))
        swap_button = wx.Button(panel, label=_("Swap"))
        close_button = wx.Button(panel, wx.ID_CLOSE, _("Close"))

        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        swap_button.Bind(wx.EVT_BUTTON, self.on_swap)
        close_button.Bind(wx.EVT_BUTTON, lambda event: self.Close())

        buttons.Add(convert_button, 0, wx.ALL, 5)
        buttons.Add(swap_button, 0, wx.ALL, 5)
        buttons.AddStretchSpacer()
        buttons.Add(close_button, 0, wx.ALL, 5)

        main.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 7)

        panel.SetSizer(main)
        self.refresh_history()

    def index_for_code(self, code):
        code = str(code).upper()
        for index, (item_code, _name) in enumerate(currency.get_currencies()):
            if item_code == code:
                return index
        return 0

    def selected_source(self):
        return currency.code_from_choice(self.source.GetStringSelection())

    def selected_target(self):
        return currency.code_from_choice(self.target.GetStringSelection())

    def save_state(self):
        self.data["last_amount"] = self.amount.GetValue()
        self.data["last_source"] = self.selected_source()
        self.data["last_target"] = self.selected_target()
        storage.save_data(self.data)

    def refresh_history(self):
        self.history.DeleteAllItems()
        history = storage.get_history()

        if not history:
            self.history.InsertItem(0, _("There are no conversions yet."))
            return

        for item in history:
            self.history.InsertItem(self.history.GetItemCount(), item)

    def convert_now(self):
        amount = currency.parse_amount(self.amount.GetValue())
        result = currency.convert(amount, self.selected_source(), self.selected_target())
        message = currency.result_message(result)
        self.data["last_amount"] = self.amount.GetValue()
        self.data["last_source"] = self.selected_source()
        self.data["last_target"] = self.selected_target()
        storage.add_history_item(message)
        storage.save_data(self.data)
        self.refresh_history()
        return message

    def on_convert(self, event):
        try:
            message = self.convert_now()
            ui.message(message)
        except Exception as e:
            error(self, str(e))

    def on_swap(self, event):
        source = self.source.GetSelection()
        target = self.target.GetSelection()
        self.source.SetSelection(target)
        self.target.SetSelection(source)
        self.save_state()
        ui.message(_("Currencies swapped."))

    def on_read_result(self, event):
        ui.message(storage.get_last_result_message())

    def on_privacy(self, event):
        info(
            self,
            _(
                "This add-on queries the public Frankfurter API to get exchange rates. "
                "It sends the amount and the selected currencies. It does not send personal information.\n\n"
                "The last values used are stored locally in NVDA's configuration. "
                "The recent conversion history is kept only for the current NVDA session and is cleared "
                "when NVDA is closed or restarted."
            )
        )

    def on_about(self, event):
        info(
            self,
            _(
                "Currency converter for NVDA.\n\n"
                "Converts amounts between currencies using Frankfurter API.\n\n"
                "Results are approximate and may not match bank fees, commercial rates or exchange offices.\n\n"
                "Version 1.2.1.\n\n"
                "Created by Arash: https://ancadper.com"
            )
        )

    def on_close(self, event):
        try:
            self.save_state()
        except Exception:
            pass

        if callable(self.on_close_callback):
            self.on_close_callback()

        self.Destroy()
