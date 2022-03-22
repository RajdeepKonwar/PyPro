from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import pandas as pd
import PySimpleGUI as sg
from ScriptParser import Parser, LogParser
from ScriptRunner import Runner

def create_plot(title, ylabel, xvals, yvals):
    plt.plot(xvals, yvals, color = 'green', marker = '.')
    plt.title(title, fontsize = 12)
    plt.xlabel('Line Number', fontsize = 10)
    plt.ylabel(ylabel, fontsize = 10)
    plt.grid(True)
    return plt.gcf()

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill = 'both', expand=1)
    return figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')

def main():
    sg.theme('LightGreen')

    layout1 = [[sg.Frame('Output', font = 'Any 15', layout = [[sg.Output(size = (150, 30), font = 'Courier 10')]])]]

    layout2 = [[sg.Canvas(size = (200, 25), key="-CANVAS1-")]]

    layout3 = [[sg.Canvas(size = (200, 25), key="-CANVAS2-")]]

    table_headers = {'Line #':[], 'Code':[], 'Time Taken (s)':[], 'CPU Usage (%)':[], 'RAM Usage (MB)':[]}
    table_data = pd.DataFrame(table_headers)
    table_headings = list(table_headers)
    table_values = table_data.values.tolist()

    layout4 = [[sg.Table(values = table_values, headings = table_headings, max_col_width = 25,
                auto_size_columns = False, size = 25,
                display_row_numbers = False, col_widths = 25,
                justification = 'left', expand_x = True, def_col_width = 25,
                num_rows = 25,
                key = '-TABLE-',
                row_height = 20)]]

    layout = [[sg.Text('Python Profiler', font = 'Any 15')],
              [sg.Text('Input Python Script'), sg.Input(key = '-INPUTFILE-', size = (150, 1)),
               sg.FileBrowse(file_types = (("Python Files", "*.py"),))],
              [sg.TabGroup([[sg.Tab('Output', layout1, key = '-TAB1-'),
                             sg.Tab('Time Taken', layout2, key = '-TAB2-', element_justification = 'center'),
                             sg.Tab('Energy Consumed', layout3, key = '-TAB3-', element_justification = 'center'),
                             sg.Tab('Hotspots', layout4, key = '-TAB4-')]],
                             tab_location = 'center', title_color = 'White',
                             tab_background_color = 'Green', selected_title_color = 'White',
                             selected_background_color = 'Gray', key = '-TABGROUP-', enable_events = True)],
              [sg.Button('Run + Profile', bind_return_key = True),
               sg.Button('Quit', button_color = ('white', 'firebrick3')) ],
              [sg.Text('Bears N\' Roses', auto_size_text = True, font = 'Courier 8')]]

    fig1 = None
    fig2 = None
    time_list = pd.DataFrame()
    cpu_list  = pd.DataFrame()
    ram_list  = pd.DataFrame()
    window = sg.Window('PyPro', layout, finalize = False, element_justification = 'left')

    while True:
        event, values = window.read()
        if event in ('Exit', 'Quit', None):
            if os.path.exists("tmp.py"):
                os.remove("tmp.py")
            break

        if event == 'Run + Profile':
            try:
                parser = Parser(values['-INPUTFILE-'])
                tmp_file = parser.Parse()

                runner = Runner(tmp_file)
                runner.Run()

                log_parser = LogParser()
                time_list = log_parser.ParseTimeLog()
                cpu_list  = log_parser.ParseCPULog()
                ram_list  = log_parser.ParseRAMLog()

                table_data = pd.DataFrame({'Line':time_list['Line'], 'Code':time_list['Code'], 'Time':time_list['Time'], 'CPU':cpu_list['CPU'], 'RAM':ram_list['RAM']})

                if window:
                    window.Refresh()
            except:
                sg.PopupError('Oops! Something went wrong!')
        elif event == '-TABGROUP-':
            active_tab = window['-TABGROUP-'].Get()
            if active_tab == '-TAB1-':
                if fig1:
                    delete_fig_agg(fig1)
                if fig2:
                    delete_fig_agg(fig2)
            elif active_tab == '-TAB2-':
                if fig2:
                    delete_fig_agg(fig2)

                if not time_list.empty:
                    fig1 = draw_figure(window['-CANVAS1-'].TKCanvas, create_plot('Time Taken', 'Time (s)', time_list['Line'], time_list['Time']))
            elif active_tab == '-TAB3-':
                if fig1:
                    delete_fig_agg(fig1)

                if not cpu_list.empty:
                    fig2 = draw_figure(window['-CANVAS2-'].TKCanvas, create_plot('Energy Consumed', 'CPU Usage (%)', cpu_list['Line'], cpu_list['CPU']))
            elif active_tab == '-TAB4-':
                if fig1:
                    delete_fig_agg(fig1)
                if fig2:
                    delete_fig_agg(fig2)

                if not table_data.empty and window:
                    window['-TABLE-'].update(values = table_data.values.tolist())
                    window.Refresh()

if __name__ == '__main__':
    main()
