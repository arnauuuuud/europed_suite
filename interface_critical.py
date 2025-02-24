#!/usr/local/depot/Python-3.7/bin/python
# /usr/local/depot/Python-3.5.1/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
import traceback
from PyQt5.QtWidgets import (
    QApplication, QWidget, QRadioButton, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QLineEdit, QPushButton, QButtonGroup,QScrollArea 
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from europed_suite import useful_recurring_functions, global_functions, pedestal_values, europed_analysis
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import math
import numpy as np

markers = ['.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd']
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'gold', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'lime', 'teal', 'navy', 'sky blue', 'lavender', 'peach', 'maroon', 'turquoise', 'gold', 'silver', 'indigo', 'violet', 'burgundy', 'mustard', 'ruby', 'emerald', 'sapphire', 'amethyst']



def run(europed_names, y_parameter, crit, crit_values, list_consid_mode, shown, showlegend, whichxparameter, xlabel, is_frac):

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

    print()
    print('#######################')
    print(f'List of runs:     {europed_names}')
    print(f'Criterion:        {crit}')
    print(f'Critical value:   {crit_values}')
    print(f'Modes considered: {list_consid_mode}')
    print(f'Show n:           {shown}')
    print(f'Y axis:           {y_parameter}')
    print('#######################')
    print()



    array_4d_y = np.zeros((len(euroname_1), len(euroname_2), len(euroname_3), len(euroname_4)))
    array_4d_n = np.zeros((len(euroname_1), len(euroname_2), len(euroname_3), len(euroname_4)))
    array_4d_frac = np.zeros((len(euroname_1), len(euroname_2), len(euroname_3), len(euroname_4)))

    array_4d_y[:,:,:,:] = None
    array_4d_n[:,:,:,:] = None
    array_4d_frac[:,:,:,:] = None

    counter = 0
    for crit_value in crit_values:
        crit_value = float(crit_value)
        for i1,e1 in enumerate(euroname_1):
            for i2,e2 in enumerate(euroname_2):
                for i3,e3 in enumerate(euroname_3):
                    for i4,e4 in enumerate(euroname_4):
                        europed_name = e1+e2+e3+e4

                        try:

                            x_param = europed_analysis.get_x_parameter(europed_name, y_parameter)
                            deltas = europed_analysis.get_x_parameter(europed_name, 'delta')
                            dict_gamma = europed_analysis.get_filtered_dict(europed_name, crit, list_consid_mode)

                            has_unstable, y_crit, mode = europed_analysis.find_critical(x_param, deltas, dict_gamma, crit_value)
                            if y_crit is  None:
                                raise useful_recurring_functions.CustomError(f"No critical value found")


                            if is_frac:
                                array_4d_frac[i1,i2,i3,i4] = pedestal_values.nesep_neped(europed_name, crit=crit, crit_value=crit_value, list_consid_mode=list_consid_mode)

                            array_4d_y[i1,i2,i3,i4] = y_crit                 
                            array_4d_n[i1,i2,i3,i4] = mode


                        except useful_recurring_functions.CustomError as e:
                            print(e)
                            pass
                        except FileNotFoundError as e:
                            print(e)
                            pass
                        except IndexError as e:
                            print(e)
                            pass
                        except KeyError as e:
                            print(e)
                            pass


        if whichxparameter == 2:
            x_list = np.array([float(e2) for e2 in euroname_2])
            y_lists = [array_4d_y[i1,:,i3,i4] for i1 in range(len(euroname_1)) for i3 in range(len(euroname_3)) for i4 in range(len(euroname_4))]
            n_lists = [array_4d_n[i1,:,i3,i4] for i1 in range(len(euroname_1)) for i3 in range(len(euroname_3)) for i4 in range(len(euroname_4))]

            temp_euroname1_forlabel = [''] if len(euroname_1) ==  1 else euroname_1
            temp_euroname3_forlabel = [''] if len(euroname_3) ==  1 else euroname_3
            temp_euroname4_forlabel = [''] if len(euroname_4) ==  1 else euroname_4

            labels = [l1 + l3 + l4 for l1 in temp_euroname1_forlabel for l3 in temp_euroname3_forlabel for l4 in temp_euroname4_forlabel]
    
        elif whichxparameter == 3:
            x_list = np.array([float(e3) for e3 in euroname_3])
            if is_frac:
                x_lists = [array_4d_frac[i1,i2,:,i4] for i1 in range(len(euroname_1)) for i2 in range(len(euroname_2)) for i4 in range(len(euroname_4))]
            y_lists = [array_4d_y[i1,i2,:,i4] for i1 in range(len(euroname_1)) for i2 in range(len(euroname_2)) for i4 in range(len(euroname_4))]
            n_lists = [array_4d_n[i1,i2,:,i4] for i1 in range(len(euroname_1)) for i2 in range(len(euroname_2)) for i4 in range(len(euroname_4))]

            temp_euroname1_forlabel = [''] if len(euroname_1) ==  1 else euroname_1
            temp_euroname2_forlabel = [''] if len(euroname_2) ==  1 else euroname_2
            temp_euroname4_forlabel = [''] if len(euroname_4) ==  1 else euroname_4

            labels = [l1 + l2 + l4 for l1 in temp_euroname1_forlabel for l2 in temp_euroname2_forlabel for l4 in temp_euroname4_forlabel]

        elif whichxparameter == 4:
            x_list = np.array([float(e4) for e4 in euroname_4])
            y_lists = [array_4d_y[i1,i2,i3,:] for i1 in range(len(euroname_1)) for i2 in range(len(euroname_2)) for i3 in range(len(euroname_3))]
            n_lists = [array_4d_n[i1,i2,i3,:] for i1 in range(len(euroname_1)) for i2 in range(len(euroname_2)) for i3 in range(len(euroname_3))]

            temp_euroname1_forlabel = [''] if len(euroname_1) ==  1 else euroname_1
            temp_euroname2_forlabel = [''] if len(euroname_2) ==  1 else euroname_2
            temp_euroname3_forlabel = [''] if len(euroname_3) ==  1 else euroname_3

            labels = [l1 + l2 + l3 for l1 in temp_euroname1_forlabel for l2 in temp_euroname2_forlabel for l3 in temp_euroname3_forlabel]

        
        for i,(y_list,n_list,label) in enumerate(zip(y_lists, n_lists,labels)):
            try:
                nan_indices = np.isnan(y_list)
                x_list_plot = x_list[~nan_indices]
                if is_frac:
                    x_list_plot = x_lists[i][~nan_indices]
                y_list = y_list[~nan_indices]
                n_list = n_list[~nan_indices]
                plot_ax.plot(x_list_plot, y_list, marker='o', label=label, color=colors[counter])
                if len(x_list_plot)>1:
                    counter += 1
                if shown:
                    for x,y,n in zip(x_list_plot,y_list,n_list):
                        if n is None:
                            n = -1
                        if not np.isnan(x) and not np.isnan(y):
                            plot_ax.annotate(int(n), (x, y), textcoords="offset points", fontsize=13, xytext=(0,5), ha='center') 
            except TypeError as e:
                print(e)


    
    y_label = global_functions.get_critical_plot_label(y_parameter)
    plot_ax.set_ylabel(y_label)

    if xlabel is not None:
        plot_ax.set_xlabel(xlabel)


    plot_ax.set_ylim(bottom=0)

    xlimleft = plot_ax.get_xlim() [0]
    if xlimleft > 0:
        plot_ax.set_xlim(left=0)

    if showlegend:
        plt.legend()

    plot_canvas.draw()
    plt.ion()



def on_button_click():
    # Get the selected radio button text
    if radio_button_alpha.isChecked():
        y_parameter = "alpha_helena_max"
    elif radio_button_teped.isChecked():
        y_parameter = "teped"
    elif radio_button_delta.isChecked():
        y_parameter = "delta"
    elif radio_button_ptot.isChecked():
        y_parameter = "pped"
    elif radio_button_peped.isChecked():
        y_parameter = "peped"
    elif radio_button_neped.isChecked():
        y_parameter = "neped"
    elif radio_button_oldpeped.isChecked():
        y_parameter = "peped_product"
    else:
        print("No x parameter is selected, alpha is used")
        y_parameter = "alpha_helena_max"

    is_frac = False
    x_label = None
    if xaxis_button_eta.isChecked():
        x_label = global_functions.eta_label
    if xaxis_button_delta.isChecked():
        x_label = global_functions.rs_label
    if xaxis_button_frac.isChecked():
        x_label = global_functions.nesepneped_label
        is_frac = True
    if xaxis_button_neped.isChecked():
        x_label = global_functions.neped_label
    if xaxis_button_betap.isChecked():
        x_label = global_functions.betap_label


    # Get the selected radio button text
    if radio_button_diamag.isChecked():
        crit = "diamag"
        crit_value_edit.setText('0.25')
    elif radio_button_alfven.isChecked():
        crit = "alfven"    
    elif radio_button_omega.isChecked():
        crit = "omega"

    if choice_button_2.isChecked():
        whichxparameter = 2
    if choice_button_3.isChecked():
        whichxparameter = 3
    if choice_button_4.isChecked():
        whichxparameter = 4


    list_consid_mode = []
    for checkbox in checkboxes_n:
        if checkbox.isChecked():
            list_consid_mode.append(int(checkbox.text()))


    showlegend = checkbox_legend.isChecked()
    showcritn = checkbox_critn.isChecked()
    crit_values = useful_recurring_functions.parse_modes(crit_value_edit.text())

    text_values = []
    for line_edit in line_edits:
        text_values.append(line_edit.text())

    # Update the plot with new data
    try:
        run(text_values, y_parameter, crit, crit_values, list_consid_mode, showcritn, showlegend, whichxparameter, x_label, is_frac)
    except Exception as e:
        print()
        print(f'    AN EXCEPTION WAS RAISED: {e}')
        print()
        traceback.print_exc()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the main window
    main_window = QWidget()
    main_window.setWindowTitle('Critical values')


    # Create radio buttons for x-axis parameters
    group_yaxis = QButtonGroup()
    y_axis_label = QLabel("Y-axis parameter")
    radio_button_alpha = QRadioButton('alpha')
    radio_button_teped = QRadioButton('teped')
    radio_button_delta = QRadioButton('width')
    radio_button_ptot = QRadioButton('pped')
    radio_button_peped = QRadioButton('peped')
    radio_button_neped = QRadioButton('neped')
    radio_button_oldpeped = QRadioButton('peped_product')
    group_yaxis.addButton(radio_button_alpha)
    group_yaxis.addButton(radio_button_teped)
    group_yaxis.addButton(radio_button_delta)
    group_yaxis.addButton(radio_button_ptot)
    group_yaxis.addButton(radio_button_peped)
    group_yaxis.addButton(radio_button_neped)
    group_yaxis.addButton(radio_button_oldpeped)
    radio_button_alpha.setChecked(True)

    # Create radio buttons for criteria
    group_crit = QButtonGroup()
    criterion_label = QLabel("Criterion")
    radio_button_diamag = QRadioButton("Diamagnetic")
    radio_button_diamag.clicked.connect(updateDiamag)
    radio_button_alfven = QRadioButton("Alfvén")
    radio_button_alfven.clicked.connect(updateAlfven)
    radio_button_omega = QRadioButton("Omega")
    group_crit.addButton(radio_button_diamag)
    group_crit.addButton(radio_button_alfven)
    group_crit.addButton(radio_button_omega)
    radio_button_alfven.setChecked(True)
    crit_value_edit = QLineEdit()
    crit_value_edit.setText('0.03')

    # Create checkboxes for 'n' values
    check_all_button = QPushButton("All")
    none_button = QPushButton("None")
    check_all_button.clicked.connect(checkAll)
    none_button.clicked.connect(uncheckAll)
    n_label = QLabel("n")
    checkboxes_n = [QCheckBox(str(n_value)) for n_value in [1, 2, 3, 4, 5, 7, 10, 20, 30, 40, 50]]
    for checkbox in checkboxes_n:
        checkbox.setChecked(True)

    # Create line edit widgets
    line_edits = [QLineEdit() for _ in range(4)]
    line_edits[0].setText('tan_eta0,tan_eta1')
    line_edits[1].setText('_rs')
    line_edits[2].setText('0.0,0.01,0.02,0.022,0.03,0.04')
    line_edits[3].setText('_neped2.57_betap1.3')


    choice_label = QLabel("X-axis")
    group_choice = QButtonGroup()
    choice_button_2 = QRadioButton("2")
    choice_button_3 = QRadioButton("3")
    choice_button_4 = QRadioButton("4")
    choice_button_2.setChecked(True)
    group_choice.addButton(choice_button_2)
    group_choice.addButton(choice_button_3)
    group_choice.addButton(choice_button_4)

    xaxis_label = QLabel("X-axis label")
    group_xaxis = QButtonGroup()
    xaxis_button_eta = QRadioButton("eta")
    xaxis_button_delta = QRadioButton("delta")
    xaxis_button_frac = QRadioButton("frac")
    xaxis_button_neped = QRadioButton("neped")
    xaxis_button_betap = QRadioButton("betap")
    group_xaxis.addButton(xaxis_button_eta)
    group_xaxis.addButton(xaxis_button_delta)
    group_xaxis.addButton(xaxis_button_frac)
    group_xaxis.addButton(xaxis_button_neped)
    group_xaxis.addButton(xaxis_button_betap)

    # Create widgets for the rest of the parameters
    empty_label = QLabel("")
    checkbox_legend = QCheckBox('Legend')
    checkbox_critn = QCheckBox("Critical n")

    # Create a button
    plot_button = QPushButton('Plot')
    plot_button.clicked.connect(on_button_click)

    # Create a Matplotlib plot
    fig, plot_ax = plt.subplots()
    plot_canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(plot_canvas,plot_canvas)

    # Layouts
    yparam_layout = QVBoxLayout()
    yparam_layout.addWidget(y_axis_label)
    yparam_layout.addWidget(radio_button_alpha)
    yparam_layout.addWidget(radio_button_delta)
    yparam_layout.addWidget(radio_button_teped)
    yparam_layout.addWidget(radio_button_ptot)
    yparam_layout.addWidget(radio_button_peped)
    yparam_layout.addWidget(radio_button_neped)
    yparam_layout.addWidget(radio_button_oldpeped)

    crit_layout = QVBoxLayout()
    crit_layout.addWidget(criterion_label)
    crit_layout.addWidget(radio_button_diamag)
    crit_layout.addWidget(radio_button_alfven)
    crit_layout.addWidget(radio_button_omega)
    crit_layout.addWidget(crit_value_edit)

    n_layout = QVBoxLayout()
    n_layout.addStretch()
    n_layout.addWidget(n_label)
    n_layout.addWidget(check_all_button)
    n_layout.addWidget(none_button)
    for checkbox in checkboxes_n:
        n_layout.addWidget(checkbox)
    n_layout.addStretch()
    
    choice_layout = QHBoxLayout()
    choice_layout.addWidget(choice_label)
    choice_layout.addWidget(choice_button_2)
    choice_layout.addWidget(choice_button_3)  
    choice_layout.addWidget(choice_button_4)  

    xaxis_layout = QHBoxLayout()
    xaxis_layout.addWidget(xaxis_label)
    xaxis_layout.addWidget(xaxis_button_eta)
    xaxis_layout.addWidget(xaxis_button_delta)
    xaxis_layout.addWidget(xaxis_button_frac)
    xaxis_layout.addWidget(xaxis_button_neped)
    xaxis_layout.addWidget(xaxis_button_betap)

    text_layout = QVBoxLayout()
    for line_edit in line_edits:
        text_layout.addWidget(line_edit)
    text_layout.addLayout(choice_layout)
    text_layout.addLayout(xaxis_layout)

    rest_layout = QVBoxLayout()
    rest_layout.addWidget(empty_label)
    rest_layout.addWidget(checkbox_legend)
    rest_layout.addWidget(checkbox_critn)

    button_layout = QVBoxLayout()
    button_layout.addWidget(plot_button)

    column_layout = QVBoxLayout()
    column_layout.addLayout(yparam_layout)
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


