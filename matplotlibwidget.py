from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import MouseEvent


class MatplotlibWidget(QWidget):
    plot_clicked = pyqtSignal(float) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(Figure())
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.click_mode = False

        self.is_dragging = False
        self.previous_x = None
        self.previous_y = None
        self.drag_factor = 0.0001
        self.drag_mode = "both"
        self.marker_artists = []  

        
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    # def add_marker(self, x_data, y_data, color='red', label_text=None):
    #     marker, = self.ax.plot(x_data, y_data, marker='o', color=color)

    #     if label_text:
    #         label = self.ax.annotate(label_text, (x_data, y_data),
    #                                 textcoords="offset points",
    #                                 xytext=(5, 5),
    #                                 ha='left',
    #                                 fontsize=9,
    #                                 color=color,
    #                                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1))
    #     else:
    #         label = None

    #     self.marker_artists.append((marker, label))

    #     self.canvas.draw()

    def add_marker(self, x_data, y_data, color='red'):
        marker, = self.ax.plot(x_data, y_data, marker='o', color=color)

        self.marker_artists.append((marker))

        self.canvas.draw()


    
    def plot_csv(self, data):
        self.canvas.figure.clear()
        self.ax = self.canvas.figure.subplots()
        self.ax.clear()  

        self.ax.set_title("Depth Data")
        self.ax.set_xlabel("Scanning points")
        self.ax.set_ylabel("Measurement in meters")

        
        data.plot(ax=self.ax)

        
        y_min = data.min()
        y_max = data.max()
        margin = 0.5  

        self.ax.set_ylim(y_min - margin, y_max + margin)  

        
        self.ax.relim()
        self.ax.autoscale_view()

    
        self.ax.grid(True, linestyle="--", alpha=0.7)
        self.canvas.draw()


    def activate_clicking(self):
        self.click_mode = True

    def on_click(self, event):
        if self.click_mode and event.inaxes is not None:
            y_data = event.ydata
            x_data = event.xdata

            if x_data is not None and y_data is not None:
                marker_color = self.marker_color if hasattr(self, 'marker_color') else 'red'

                self.ax.plot(x_data, y_data, marker='o', color=marker_color)
                self.canvas.draw()

                self.plot_clicked.emit(y_data)
                self.click_mode = False



    def on_press(self, event: MouseEvent):
        if event.inaxes:
            
            self.is_dragging = True
            self.previous_x = event.x
            self.previous_y = event.y

    def on_motion(self, event: MouseEvent):
        if self.is_dragging and event.inaxes and self.previous_x is not None:
            dx = event.x - self.previous_x
            dy = event.y - self.previous_y

            # Convert pixel movement to data coordinates
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            width = self.canvas.width()
            height = self.canvas.height()

            dx_data = -dx * (x_range / width)
            dy_data = -dy * (y_range / height)

            if self.drag_mode == "both":
                self.ax.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
                self.ax.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)
            elif self.drag_mode == "horizontal":
                self.ax.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
            elif self.drag_mode == "vertical":
                self.ax.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)

            self.previous_x = event.x
            self.previous_y = event.y

            self.canvas.draw()



    def on_release(self, event: MouseEvent):
          
        if event.inaxes:
            self.is_dragging = False
            self.previous_x = None
            self.previous_y = None

    def on_scroll(self, event: MouseEvent):
        
        if event.inaxes:  
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
 
           
            mouse_x, mouse_y = event.xdata, event.ydata

            
            zoom_factor = 1.1
            if event.button == 'up':  
                scale_factor = 1 / zoom_factor
            elif event.button == 'down': 
                scale_factor = zoom_factor

            
            new_xlim = [
                mouse_x - (mouse_x - xlim[0]) * scale_factor,
                mouse_x + (xlim[1] - mouse_x) * scale_factor,
            ]
            new_ylim = [
                mouse_y - (mouse_y - ylim[0]) * scale_factor,
                mouse_y + (ylim[1] - mouse_y) * scale_factor,
            ]

           
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)

           
            self.canvas.draw()
