# Project GUI - test. For SystemC Models

import os
from os import walk
import wx
from wx import *
import wx.dataview
import wx.xrc
import wx.lib.mixins.listctrl as listmix

# Globals for display
WIN_SIZE_HOR_MAX = 1280
WIN_SIZE_VER_MAX = 720
WIN_SIZE_HOR_MIN = 1280
WIN_SIZE_VER_MIN = 720

BTN_SIZE_HOR = 60
BTN_SIZE_VER = 30

# Default paths
PATH_TEST_CASE = "." + os.sep + "TL_TESTS" + os.sep + "TOP_LEVEL_TEST_stim_tcase.cpp"
PATH_TOP_LEVEL = "." + os.sep + "TL_lib" + os.sep + "TOP_LEVEL.cpp"
PATH_FI_LIBRARY = "." + os.sep + "FI_lib" + os.sep
NAME_TOP_LEVEL_MODULE = "TOP_LEVEL"

# Global Arrays
f_tl_signals = []
f_tl_ports = []
f_tl_components = []
f_fi_faults = []


########################################################################
class MainPanel(wx.Panel, listmix.ColumnSorterMixin):
    # ----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # ------------------------------------------------------------ #
        # File and Folder Pickers
        self.t_filePicker_tl = wx.StaticText( self, wx.ID_ANY, u" Top Level Source:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_filePicker_tl = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.cpp",
                                               wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)

        self.t_filePicker_tc = wx.StaticText( self, wx.ID_ANY, u" Test Stimulus File:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_filePicker_tc = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.cpp",
                                               wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)

        self.t_dirPicker_fi = wx.StaticText( self, wx.ID_ANY, u" Fault Injection Lib:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_dirPicker_fi = wx.DirPickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select the FI Library Folder",
                                               wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)

        # ------------------------------------------------------------ #
        # Buttons and Bindings
        self.btn_parse = wx.Button(self, label="PARSE", pos=(900, 50), size=(BTN_SIZE_HOR, BTN_SIZE_VER) )
        #self.btn_create = wx.Button(self, label="EXIT", pos=(140, 10), size=(BTN_SIZE_HOR, BTN_SIZE_VER) )
        self.Bind(wx.EVT_BUTTON, self.f_m_btn_parse, self.btn_parse)


        # ------------------------------------------------------------ #
        # Create All lists
        self.list_ctrl_components = wx.ListCtrl(self, pos=(50, 200), size=(300, 500),
                                                style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.list_ctrl_components.InsertColumn(0, "TYPE")
        self.list_ctrl_components.InsertColumn(1, "COMPONENT", width=LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl_components.Bind(wx.EVT_LIST_ITEM_SELECTED, self.list_ctrl_component_click)

        self.list_ctrl_ports = wx.ListCtrl(self, pos=(450, 200), size=(200, 500),
                                           style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.list_ctrl_ports.InsertColumn(0, "ALL PORTS", width=LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl_ports.Bind(wx.EVT_LIST_ITEM_SELECTED, self.list_ctrl_ports_click)

        self.list_ctrl_faults = wx.ListCtrl(self, pos=(550, 200), size=(200, 500),
                                           style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.list_ctrl_faults.InsertColumn(0, "POSSIBLE FAULTS", width=LIST_AUTOSIZE_USEHEADER)


        # ------------------------------------------------------------ #
        # Create Sizer and add to it
        sizer_pathLabels = wx.BoxSizer(wx.VERTICAL)
        sizer_pathPickers = wx.BoxSizer(wx.VERTICAL)
        sizer_paths = wx.BoxSizer(wx.HORIZONTAL)
        sizer_lists = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main = wx.BoxSizer(wx.VERTICAL)

        sizer_pathLabels.Add(self.t_filePicker_tl, 0, wx.TOP | wx.ALIGN_TOP, 10)
        sizer_pathLabels.Add(self.t_filePicker_tc, 0, wx.TOP | wx.ALIGN_LEFT, 20)
        sizer_pathLabels.Add(self.t_dirPicker_fi, 0, wx.TOP | wx.ALIGN_TOP, 20)

        sizer_pathPickers.Add(self.m_filePicker_tl, 0, wx.ALL | wx.ALIGN_TOP, 5)
        sizer_pathPickers.Add(self.m_filePicker_tc, 0, wx.ALL | wx.ALIGN_TOP, 5)
        sizer_pathPickers.Add(self.m_dirPicker_fi, 0, wx.ALL | wx.ALIGN_TOP, 5)

        sizer_paths.Add(sizer_pathLabels, 0, wx.ALL | wx.ALIGN_TOP, 5)
        sizer_paths.Add(sizer_pathPickers, 0, wx.ALL | wx.ALIGN_TOP, 5)

        sizer_lists.Add(self.list_ctrl_components, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        sizer_lists.Add(self.list_ctrl_ports, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        sizer_lists.Add(self.list_ctrl_faults, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)

        sizer_main.Add(sizer_paths, 0, wx.ALL | wx.ALIGN_BOTTOM, 10)
        sizer_main.Add(sizer_lists, 0, wx.ALL | wx.ALIGN_BOTTOM, 10)

        self.SetSizer(sizer_main)

    # ============================================================ #
    # On Parsing the Top Level File
    def f_m_btn_parse(self, event):
        global f_tl_signals         # Top Level Signals
        global f_tl_ports           # Top Level Ports
        global f_tl_components      # Top Level Components
        global f_fi_faults

        # ------------------------------------------------------------ #
        # CLEARING OLD LISTS
        self.list_ctrl_components.DeleteAllItems()
        self.list_ctrl_ports.DeleteAllItems()
        self.list_ctrl_faults.DeleteAllItems()

        f_tl_signals = []
        f_tl_ports = []
        f_tl_components = []
        f_fi_faults = []

        f_tl_h = open(PATH_TOP_LEVEL[:-3] + "h")
        f_tl_h_lines = f_tl_h.readlines()
        f_tl_cpp = open(PATH_TOP_LEVEL)
        f_tl_lines = f_tl_cpp.readlines()

        for (dirpath, dirnames, filenames) in walk(PATH_FI_LIBRARY):
            f_fi_faults.extend(filenames)
            break

        f_fi_faults = [line.split('.')[0] for line in f_fi_faults]

        # ------------------------------------------------------------ #
        # FINDING TEST PORTS
        for line in f_tl_h_lines:
            line = ''.join(line.split())
            if ("sc_core::sc_out<" in line) \
                    or ("sc_core::sc_in<" in line) \
                    or ("sca_tdf::sca_out<" in line) \
                    or ("sca_tdf::sca_in<" in line):
                sig_kind = line.split("<")[0]
                sig_type = (line.split("<")[1]).split(">")[0]
                sig_name = ((line.split("<")[1]).split(">")[1]).split(";")[0]

                f_tl_signals.append([sig_kind, sig_type, sig_name])

        # ------------------------------------------------------------ #
        # FINDING SIGNALS
        for line in f_tl_lines:
            line = ''.join(line.split())
            if ("sc_core::sc_signal<" in line) or ("sca_tdf::sca_signal<" in line):
                if (";" in line) and ("(" not in line):
                    sig_kind = line.split("<")[0]
                    sig_type = (line.split("<")[1]).split(">&")[0]
                    sig_name = ((line.split("<")[1]).split(">&")[1]).split(";")[0]

                    f_tl_signals.append([sig_kind, sig_type, sig_name])

            if STR_COMP_CONSTRUCT_START in line:
                break

        # ------------------------------------------------------------ #
        # FINDING PORTS
        for line in f_tl_lines:
            line = ''.join(line.split())
            if ".bind(" in line:
                port_name = line.split(".bind(")[0]
                port_signal = (line.split(".bind(")[1]).split(");")[0]

                sig_index = [x for x in f_tl_signals if port_signal in x]

                f_tl_ports.append(
                    [port_name.split("->")[0], port_name.split("->")[1], port_signal, sig_index[0][0],
                     sig_index[0][1]])

        # ------------------------------------------------------------ #
        # ARRANGING DIGITAL & ANALOGUE PORTS
        for ports in f_tl_ports:
            if not (any(ports[0] in components for components in f_tl_components)):
                if "sca_tdf" in ports[3] or "sc_core" in ports[3]:
                    f_tl_components.append([ports[0], ports[3].split("::")[0]])
                else:
                    print("PORT TYPE NOT COMPATIBLE!")
                    print(ports)
            else:
                if ports[3].split("::")[0] not in f_tl_components[-1]:
                    if "sc_i" in ports[1] or "tdf_o" in ports[1]:
                        f_tl_components[-1:] = [[ports[0], "conv_de2tdf"]]
                    elif "tdf_i" in ports[1] or "sc_o" in ports[1]:
                        f_tl_components[-1:] = [[ports[0], "conv_tdf2de"]]

        # ------------------------------------------------------------ #
        # INSERTING IN COMPONENTS LIST
        f_tl_ports.sort(key=lambda x: x[1], reverse=False)
        f_tl_components.sort(key=lambda x: x[1], reverse=True)
        index = 0
        for components in f_tl_components:
            if "sca_tdf" in components[1]:
                self.list_ctrl_components.InsertItem(index, "ANALOG")
            elif "sc_core" in components[1]:
                self.list_ctrl_components.InsertItem(index, "DIGITAL")
            elif "conv_tdf2de" in components[1]:
                self.list_ctrl_components.InsertItem(index, "Convert A2D")
            elif "conv_de2tdf" in components[1]:
                self.list_ctrl_components.InsertItem(index, "Convert D2A")

            self.list_ctrl_components.SetItem(index, 1, components[0])
            index += 1

        # ------------------------------------------------------------ #
        f_tl_h.close()
        f_tl_cpp.close()

    # ============================================================ #
    # On Selecting a Component
    def list_ctrl_component_click(self, event):
        selected_item = self.list_ctrl_components.GetFocusedItem()
        selected_item_type = self.list_ctrl_components.GetItemText(selected_item, 0)
        selected_item_name = self.list_ctrl_components.GetItemText(selected_item, 1)

        index = 0
        self.list_ctrl_ports.DeleteAllItems()
        self.list_ctrl_faults.DeleteAllItems()
        for line in f_tl_ports:
            if selected_item_name == line[0]:
                self.list_ctrl_ports.InsertItem(index, line[1])
                index += 1

    # ============================================================ #
    # On Selecting a Port
    def list_ctrl_ports_click(self, event):
        selected_item = self.list_ctrl_components.GetFocusedItem()
        selected_item_type = self.list_ctrl_components.GetItemText(selected_item, 0)
        selected_port = self.list_ctrl_ports.GetFocusedItem()
        selected_port_name = self.list_ctrl_ports.GetItemText(selected_port, 0)

        index = 0
        self.list_ctrl_faults.DeleteAllItems()
        for line in f_fi_faults:
            if selected_item_type == "DIGITAL" and "FI_D_" in line:
                self.list_ctrl_faults.InsertItem(index, line)
                index += 1
            elif selected_item_type == "ANALOG" and "FI_A_" in line:
                self.list_ctrl_faults.InsertItem(index, line)
                index += 1
            elif "Convert" in selected_item_type:
                if "FI_D_" in line and "sc_" in selected_port_name:
                    self.list_ctrl_faults.InsertItem(index, line)
                    index += 1
                elif "FI_A_" in line and "tdf_" in selected_port_name:
                    self.list_ctrl_faults.InsertItem(index, line)
                    index += 1


########################################################################
# Main Frame Class
class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent=parent, title=title,
                          size=(WIN_SIZE_HOR_MIN, WIN_SIZE_VER_MIN))

        # ------------------------------------------------------------ #
        # Creating menu bar and menus
        self.mnu = wx.MenuBar()
        self.mnu_1 = wx.Menu()
        self.mnu_2 = wx.Menu()
        self.mnu_3 = wx.Menu()

        self.mnu_1.Append(wx.NewId(), "New...", "A new window to open")
        self.mnu_1.Append(wx.NewId(), "Open...", "Open an existing project")
        self.mnu_2.Append(wx.NewId(), "Options", "Display the available options")
        self.mnu_3.Append(wx.NewId(), "Tutorial", "Open tutorial for the tool")
        self.mnu_3.Append(wx.NewId(), "About", "Info regarding the tool and version")

        self.mnu.Append(self.mnu_1, "File")
        self.mnu.Append(self.mnu_2, "Edit")
        self.mnu.Append(self.mnu_3, "Help")
        self.SetMenuBar(self.mnu)

        # ------------------------------------------------------------ #
        # Creating status bar
        self.stb = self.CreateStatusBar(2)
        self.stb.SetStatusWidths([600, -1])
        self.stb.SetStatusText(" Main Project", 1)

        # ------------------------------------------------------------ #
        # Creating main panel and objects
        self.pnl = MainPanel(self)

        # ------------------------------------------------------------ #
        # Display The Main frame
        self.Bind(wx.EVT_CLOSE, self.f_frame_close)
        self.SetMinSize((WIN_SIZE_HOR_MIN, WIN_SIZE_VER_MIN))
        self.SetMaxSize((WIN_SIZE_HOR_MAX, WIN_SIZE_VER_MAX))
        self.Center()
        self.Show(True)

    def f_m_btn_exit(self, event):
        self.Close(True)

    def f_frame_close(self, event):
        self.Destroy()


# Main Program
if __name__ is '__main__':

    app = wx.App(False)
    frame = MainFrame(parent=None, title="FIT - Fault Injection Tool")
    app.MainLoop()
