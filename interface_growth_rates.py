#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QRadioButton, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QLineEdit, QPushButton, QButtonGroup,  QSpacerItem, QSizePolicy,QScrollArea
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from europed_suite import useful_recurring_functions, europed_analysis, global_functions
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import traceback
import math
import numpy as np

markers = [ 'D', 's', 'p', '*', 'h', 'H', '+', 'x', 'd', 'o', 'v', '^', '<', '>', '1', '2', '3', '4']
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'gold', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'lime', 'teal', 'navy', 'sky blue', 'lavender', 'peach', 'maroon', 'turquoise', 'gold', 'silver', 'indigo', 'violet', 'burgundy', 'mustard', 'ruby', 'emerald', 'sapphire', 'amethyst']




def run(europed_names, x_parameter, crit, crit_value, envelope, list_consid_mode, hline, vline, legend, fixed_width, q_ped_def, wrongslope):

    # Clear the existing plot
    plot_ax.clear()

    euroname_1 = europed_names[0].split(',')
    euroname_2 = europed_names[1].split(',')
    euroname_3 = europed_names[2].split(',')
    euroname_4 = europed_names[3].split(',')

    euroname_2 = [''] if euroname_2 == [] else euroname_2
    euroname_3 = [''] if euroname_3 == [] else euroname_3
    euroname_4 = [''] if euroname_4 == [] else euroname_4
    europed_names = [e1+e2+e3+e4 for e1 in euroname_1 for e2 in euroname_2 for e3 in euroname_3 for e4 in euroname_4]

    print('')
    print('')
    print('############### Updated parameters ###############')
    print(f'# List of runs:        {europed_names}')
    print(f'# X-axis parameter:    {x_parameter}')
    print(f'# Critical value:      {crit_value}')
    print(f'# Stability criterion: {crit}')
    print(f'# Plot envelope:       {envelope}')
    print(f'# Modes:               {list_consid_mode}')
    print(f'# Plot H-line:         {hline}')
    print(f'# Plot V-line:         {vline}')
    print('##################################################')
    print('')


    sample_points = np.linspace(0.3, 1, len(europed_names))
    colors = plt.cm.inferno_r(sample_points)

    for iplot,europed_run in enumerate(europed_names):
        try:
            x_param = europed_analysis.get_x_parameter(europed_run, x_parameter, q_ped_def)
            if not fixed_width:
                deltas = europed_analysis.get_x_parameter(europed_run, 'delta')
            else:
                deltas = europed_analysis.get_x_parameter(europed_run, 'betaped')
            # deltas = europed_analysis.get_x_parameter(europed_run, 'delta')

            # if type(res) == str and res == 'File not found':
            #     continue
            # else:
            #     x_param = res
            # gammas, modes = europed_analysis.get_gammas(europed_run, crit)
            # try:
            #     tab, consid_mode = europed_analysis.filter_tab_general(gammas, modes, list_consid_mode,[])
            # except TypeError as e:
            #     print(e)
            #     continue        
            # sorted_indices = np.argsort(x_param)
            # x_param = x_param[sorted_indices]
            # tab = tab[sorted_indices]
            
            # list_mode_to_plot = [mode for mode in list_consid_mode if mode in modes]

            dict_gamma = europed_analysis.get_gammas(europed_run, crit, fixed_width)
            dict_gamma = europed_analysis.filter_dict(dict_gamma, list_consid_mode)
            if wrongslope:
                dict_gamma = europed_analysis.remove_wrong_slope(dict_gamma)
            dict_gamma_r = europed_analysis.reverse_nested_dict(dict_gamma)

            # for mode in dict_gamma_r.keys():
            #     dict_gamma_n = dict_gamma_r[mode]
            #     x = list(dict_gamma_n.keys())
            #     y = list(dict_gamma_n.values())
            #     plot_ax.plot(x_filtered,y_filtered, color=global_functions.dict_mode_color[int(mode)], marker=markers[iplot], label=f'{europed_run} - {mode}')



            if not envelope:
                for mode in dict_gamma_r.keys():
                    dict_gamma_n = dict_gamma_r[mode]
                    deltas_to_plot = list(dict_gamma_n.keys())
                    x_to_plot = europed_analysis.give_matching_x_with_deltas(sorted(deltas), sorted(x_param), deltas_to_plot)
                    y = list(dict_gamma_n.values())
                    plot_ax.plot(x_to_plot, y, color=global_functions.dict_mode_color[int(mode)], marker=markers[iplot], label=f'{europed_run} - {mode}')
                    # plot_ax.plot(x_to_plot, y)
                # for i, mode in enumerate(list_mode_to_plot):
                #     temp_x = x_param
                #     temp_y = tab[:,i]
                #     nan_indices = np.isnan(temp_y)
                #     x_filtered = temp_x[~nan_indices]
                #     y_filtered = temp_y[~nan_indices]
                #     plot_ax.plot(x_filtered,y_filtered, color=global_functions.dict_mode_color[int(mode)], marker=markers[iplot], label=f'{europed_run} - {mode}')
            
            else:
                # dict_gamma = europed_analysis.get_gammas(europed_run, crit=crit)
                # x_parameter_list = europed_analysis.get_x_parameter(europed_run, x_parameter=x_parameter)
                # dict_gamma = europed_analysis.filter_dict(dict_gamma, list_consid_mode)
                x_envelope, y_envelope = europed_analysis.give_envelop(dict_gamma, deltas, x_parameter=x_param)
                plot_ax.plot(x_envelope, y_envelope, color=colors[iplot], label=europed_run)


            if vline:
                has_unstable, x_crit, critn = europed_analysis.find_critical(x_param, deltas, dict_gamma, crit_value)
                if has_unstable:
                    if not envelope:
                        colorvline = 'r'
                    else:
                        colorvline = colors[iplot] 
                    plot_ax.axvline(x_crit, color=colorvline, linestyle=':')
                    xmin,xmax,ymin,ymax = plot_ax.axis()
                    ratio = (x_crit-xmin)/(xmax-xmin)
                    trans = transforms.blended_transform_factory(plot_ax.transData, plot_ax.transAxes)
                    x_crit = np.abs(x_crit)
                    try:
                        x_crit_order = math.floor(math.log10(x_crit))
                        x_crit_round = np.around(np.around(x_crit*10**-x_crit_order,2)*10**x_crit_order,6)
                        plot_ax.text(x_crit, 1.0, str(x_crit_round), color=colorvline, horizontalalignment='center', verticalalignment='bottom',transform=trans)
                    except ValueError:
                        traceback.print_exc()
                        pass
        except RuntimeError:
            print(f"{europed_run:>40} RUNTIME ERROR : NO FIT FOUND")
            traceback.print_exc()
        except FileNotFoundError as e:
            print(f"FILE DOES NOT EXIST: {e}")
            traceback.print_exc()
        except IndexError as e:
            print(e)
            traceback.print_exc()
            continue


    if hline:
        plot_ax.axhline(crit_value, linestyle="--",color="k")

    x_label, y_label = global_functions.get_plot_labels_gamma_profiles(x_parameter, crit)
    plot_ax.set_xlabel(x_label)
    plot_ax.set_ylabel(y_label)
    if crit != 'omega':
        plot_ax.set_ylim(bottom=0)
    plot_ax.set_xlim(left=0)

    if legend:
        plot_ax.legend()

    plot_canvas.draw()
    plt.ion()

def checkAll(self):
    for checkbox in checkboxes_n:
        checkbox.setChecked(True)

def uncheckAll(self):
    for checkbox in checkboxes_n:
        checkbox.setChecked(False)

def updateAlfven(self):
    crit_value_edit.setText('0.03')
    
def updateDiamag(self):
    crit_value_edit.setText('0.25')

def uncheckHline(self):
    checkbox_hline.setChecked(False)

def updatewhenfixedwidth(self):
    if is_fixed_width_button.isChecked():
        line_edits[0].setText('fwa_rs0.022_betap1.3_w0.054')
    else:
        line_edits[0].setText('tan_eta0_rs0.022_neped2.57_betap1.3')

def on_button_click():
    # Get the selected radio button text
    if radio_button_alpha.isChecked():
        x_parameter = "alpha_helena_max"
    elif radio_button_teped.isChecked():
        x_parameter = "teped"
    elif radio_button_delta.isChecked():
        x_parameter = "delta"
    elif radio_button_ptot.isChecked():
        x_parameter = "pped"
    elif radio_button_peped.isChecked():
        x_parameter = "peped"
    elif radio_button_neped.isChecked():
        x_parameter = "neped"
    elif radio_button_nesepneped.isChecked():
        x_parameter = "nesep_neped"
    elif radio_button_betaped.isChecked():
        x_parameter = "betaped"
    else:
        print("No x parameter is selected, alpha is used")
        x_parameter = "alpha_helena_max"


    group_peddef.addButton(radio_button_teposdelta)
    group_peddef.addButton(radio_button_product)
    group_peddef.addButton(radio_button_fixedposition)
    group_peddef.addButton(radio_button_posteped)


    if radio_button_teposdelta.isChecked():
        q_ped_def = 'tepos-delta'
    elif radio_button_product.isChecked():
        q_ped_def = 'product'
    elif radio_button_fixedposition.isChecked():
        q_ped_def = 'fixedposition'
    elif radio_button_posteped.isChecked():
        q_ped_def = 'positionTeped'
    

    # Get the selected radio button text
    if radio_button_diamag.isChecked():
        crit = "diamag"
    elif radio_button_alfven.isChecked():
        crit = "alfven"    
    elif radio_button_omega.isChecked():
        crit = "omega"

    list_consid_mode = []
    for checkbox in checkboxes_n:
        if checkbox.isChecked():
            list_consid_mode.append(int(checkbox.text()))

    if is_fixed_width_button.isChecked():
        fixed_width = True
    else:
        fixed_width = False


    hline = checkbox_hline.isChecked()
    vline = checkbox_vline.isChecked()
    wrongslope = checkbox_wrongslope.isChecked()
    envelope = checkbox_envelope.isChecked()
    legend = checkbox_legend.isChecked()
    crit_value = float(crit_value_edit.text())

    text_values = []
    for line_edit in line_edits:
        text_values.append(line_edit.text())

    # Update the plot with new data
    try:
        run(text_values, x_parameter, crit, crit_value, envelope, list_consid_mode, hline, vline, legend, fixed_width, q_ped_def, wrongslope)
    except Exception as e:
        print()
        print(f'    AN EXCEPTION WAS RAISED: {e}')
        print()
        traceback.print_exc()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the main window
    main_window = QWidget()
    main_window.setWindowTitle('Growth rates')


    # Create radio buttons for x-axis parameters
    group_xaxis = QButtonGroup()
    x_axis_label = QLabel("X-axis parameter")
    radio_button_alpha = QRadioButton('alpha')
    radio_button_teped = QRadioButton('teped')
    radio_button_delta = QRadioButton('width')
    radio_button_ptot = QRadioButton('pped')
    radio_button_peped = QRadioButton('peped')
    radio_button_neped = QRadioButton('neped')
    radio_button_betaped = QRadioButton('betaped')
    radio_button_nesepneped = QRadioButton('nesep/neped')
    group_xaxis.addButton(radio_button_alpha)
    group_xaxis.addButton(radio_button_teped)
    group_xaxis.addButton(radio_button_delta)
    group_xaxis.addButton(radio_button_ptot)
    group_xaxis.addButton(radio_button_peped)
    group_xaxis.addButton(radio_button_neped)
    group_xaxis.addButton(radio_button_betaped)
    group_xaxis.addButton(radio_button_nesepneped)
    radio_button_alpha.setChecked(True)

    # Which pedestal definition
    group_peddef = QButtonGroup()
    peddef_label = QLabel("Pedestal definition")
    radio_button_teposdelta = QRadioButton('tepos-delta')
    radio_button_product = QRadioButton('product')
    radio_button_fixedposition = QRadioButton('fixedposition')
    radio_button_posteped = QRadioButton('positionTeped')
    group_peddef.addButton(radio_button_teposdelta)
    group_peddef.addButton(radio_button_product)
    group_peddef.addButton(radio_button_fixedposition)
    group_peddef.addButton(radio_button_posteped)
    radio_button_teposdelta.setChecked(True)

    # Create radio buttons for criteria
    group_crit = QButtonGroup()
    criterion_label = QLabel("Criterion")
    radio_button_diamag = QRadioButton("Diamagnetic")
    radio_button_diamag.clicked.connect(updateDiamag)
    radio_button_alfven = QRadioButton("Alfvén")
    radio_button_alfven.clicked.connect(updateAlfven)
    radio_button_omega = QRadioButton("Omega")
    radio_button_omega.clicked.connect(uncheckHline)
    group_crit.addButton(radio_button_diamag)
    group_crit.addButton(radio_button_alfven)
    group_crit.addButton(radio_button_omega)
    radio_button_alfven.setChecked(True)
    crit_value_edit = QLineEdit()
    crit_value_edit.setText('0.03')

    # Create button to change if fixed width
    is_fixed_width_button = QCheckBox("Fixed width")
    is_fixed_width_button.clicked.connect(updatewhenfixedwidth)

    # Create checkboxes for 'n' values
    check_all_button = QPushButton("All")
    none_button = QPushButton("None")
    check_all_button.clicked.connect(checkAll)
    none_button.clicked.connect(uncheckAll)
    n_label = QLabel("n")
    checkboxes_n = [QCheckBox(str(n_value)) for n_value in [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 30, 40, 50]]
    for checkbox in checkboxes_n:
        checkbox.setChecked(True)

    # Create line edit widgets
    line_edits = [QLineEdit() for _ in range(4)]
    line_edits[0].setText('tan_eta0_rs0.022_neped2.57_betap1.3')

    # Create widgets for the rest of the parameters
    empty_label = QLabel("")
    checkbox_hline = QCheckBox("H line")
    checkbox_vline = QCheckBox("V line")
    checkbox_wrongslope = QCheckBox("Wrong slope")
    checkbox_envelope = QCheckBox("Envelope")
    checkbox_legend = QCheckBox("Legend")
    checkbox_legend.setChecked(True)

    # Create a button
    plot_button = QPushButton('Plot')
    plot_button.clicked.connect(on_button_click)

    # Create a Matplotlib plot
    fig, plot_ax = plt.subplots()
    plot_canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(plot_canvas,plot_canvas)

    # Layouts
    xparam_layout = QVBoxLayout()
    xparam_layout.addWidget(x_axis_label)
    xparam_layout.addWidget(radio_button_alpha)
    xparam_layout.addWidget(radio_button_delta)
    xparam_layout.addWidget(radio_button_teped)
    xparam_layout.addWidget(radio_button_ptot)
    xparam_layout.addWidget(radio_button_peped)
    xparam_layout.addWidget(radio_button_neped)
    xparam_layout.addWidget(radio_button_betaped)
    xparam_layout.addWidget(radio_button_nesepneped)

    peddef_layout = QVBoxLayout()
    peddef_layout.addWidget(x_axis_label)
    peddef_layout.addWidget(radio_button_teposdelta)
    peddef_layout.addWidget(radio_button_product)
    peddef_layout.addWidget(radio_button_fixedposition)
    peddef_layout.addWidget(radio_button_posteped)

    crit_layout = QVBoxLayout()
    crit_layout.addWidget(criterion_label)
    crit_layout.addWidget(radio_button_diamag)
    crit_layout.addWidget(radio_button_alfven)
    crit_layout.addWidget(radio_button_omega)
    crit_layout.addWidget(crit_value_edit)

    n_layout = QVBoxLayout()
    n_layout.addWidget(is_fixed_width_button)
    n_layout.addStretch()
    n_layout.addLayout(peddef_layout)
    n_layout.addStretch()
    n_layout.addWidget(n_label)
    n_layout.addWidget(check_all_button)
    n_layout.addWidget(none_button)

    n_leftlayout = QVBoxLayout()
    n_rightlayout = QVBoxLayout()
    n_checkbox_layout = QHBoxLayout()
    for checkbox in checkboxes_n[::2]:
        n_leftlayout.addWidget(checkbox)
    for checkbox in checkboxes_n[1::2]:
        n_rightlayout.addWidget(checkbox)
    n_checkbox_layout.addLayout(n_leftlayout)
    n_checkbox_layout.addLayout(n_rightlayout)
    n_layout.addLayout(n_checkbox_layout)
    n_layout.addStretch()

    text_layout = QVBoxLayout()
    for line_edit in line_edits:
        text_layout.addWidget(line_edit)

    rest_layout = QVBoxLayout()
    rest_layout.addWidget(empty_label)
    rest_layout.addWidget(checkbox_hline)
    rest_layout.addWidget(checkbox_vline)
    rest_layout.addWidget(checkbox_wrongslope)
    rest_layout.addWidget(checkbox_envelope)
    rest_layout.addWidget(checkbox_legend)

    button_layout = QVBoxLayout()
    button_layout.addWidget(plot_button)

    column_layout = QVBoxLayout()
    column_layout.addLayout(xparam_layout)
    column_layout.addLayout(crit_layout)
    column_layout.addLayout(rest_layout)

    line_layout = QHBoxLayout()
    line_layout.addLayout(column_layout)
    line_layout.addLayout(n_layout)

    right_layout = QVBoxLayout()
    right_layout.addLayout(text_layout)
    right_layout.addLayout(line_layout)
    right_layout.addLayout(button_layout)
    right_layout.addStretch()

    left_layout = QVBoxLayout()
    left_layout.addWidget(toolbar)
    left_layout.addWidget(plot_canvas)


    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_widget = QWidget()
    scroll_layout = right_layout
    scroll_widget.setLayout(scroll_layout)
    scroll_area.setWidget(scroll_widget)

    main_layout = QHBoxLayout()
    main_layout.addLayout(left_layout,2)
    main_layout.addWidget(scroll_area, 1)


    main_window.setLayout(main_layout)
    main_window.show()
    sys.exit(app.exec_())


