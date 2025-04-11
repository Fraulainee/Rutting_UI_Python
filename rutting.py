import sys, os, tempfile, folium, csv
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton, QVBoxLayout, QWidget
from matplotlibwidget import MatplotlibWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('/home/lab/Documents/rutting/maingui.ui', self)
        
        self.webview = QWebEngineView()

        self.y_data_1 = None
        self.y_data_2 = None
        
        self.current_target_label = None
        self.df = None
        self.current_row = 0
        self.automate_activated = False
        self.scanning_point_start = 0.0
        self.scanning_point_end = 0, 0

        self.plot_frame = self.findChild(MatplotlibWidget, "plotwidget")  

        
        self.importcsvbtn.clicked.connect(self.import_csv)
        self.nextbtn.clicked.connect(self.update_current_row) 
        self.backbtn.clicked.connect(self.show_previous_row)
        self.resetbtn.clicked.connect(self.reset_all)  
        self.undobtn.clicked.connect(self.reset_plot)
        self.startbtn.clicked.connect(self.activate_automate)
        self.plotrowbtn.clicked.connect(self.plot_specific_row)  
        self.savedatabtn.clicked.connect(self.save_data)
        self.maximumheightbtn.clicked.connect(self.activate_maximum_btn)
        self.minimumheightbtn.clicked.connect(self.activate_minimum_btn)
        self.plot_frame.plot_clicked.connect(self.update_label)
        self.setup_map(0,0)

    def activate_automate(self):
        if self.df is not None:
            self.automate_activated = True
            self.scanning_point_start = int(self.start_line_edit.text()) 
            self.scanning_point_end = int(self.end_line_edit.text())

            self.get_row(self.current_row)


    def calculate_automate_markers(self, row_index, scanning_point_start, scanning_point_end):
        if self.df is not None:
            row_data = self.df.iloc[row_index]
            fields = [f"field{i}" for i in range(scanning_point_start, scanning_point_end + 1)]  
            row_data_filtered = row_data[fields]

            try:
                max_value = row_data_filtered.max()
                min_value = row_data_filtered.min()

                max_index = row_data_filtered.idxmax()
                min_index = row_data_filtered.idxmin()

                # self.plot_frame.add_marker(max_index, max_value, color='#0000FF', label_text='Max')
                # self.plot_frame.add_marker(min_index, min_value, color='#FF8C00', label_text='Min')

                self.plot_frame.add_marker(max_index, max_value, color='#0000FF')
                self.plot_frame.add_marker(min_index, min_value, color='#FF8C00')


                self.y_data_1 = max_value
                self.y_data_2 = min_value

                difference = max_value - min_value
                self.max_automate.setText(f"{max_value}")
                self.min_automate.setText(f"{min_value}")
                self.total_automate.setText(f"{difference}")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to calculate markers:\n{str(e)}")

       

            
                     

    def activate_maximum_btn(self):
        self.current_target_label = self.maxheightvalue  
        self.plot_frame.activate_clicking()
        self.plot_frame.marker_color = '#0000FF'  

        self.maximumheightbtn.setStyleSheet("""
            QPushButton {
                background-color: #0000FF;  /* Blue */
                color: white;
            }
            QPushButton:hover {
                background-color: #5F9EA0;
            }
        """) 

    def activate_minimum_btn(self):
        self.current_target_label = self.minheightvalue  
        self.plot_frame.activate_clicking()
        self.plot_frame.marker_color = '#FF8C00'  # Orange for min

        self.minimumheightbtn.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;  /* Dark Orange */
                color: white;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
        """)

    def update_label(self, y_data):
        if self.current_target_label:
            self.current_target_label.setText(f"{y_data}")
            
            if self.current_target_label == self.maxheightvalue:
                self.y_data_1 = y_data
            elif self.current_target_label == self.minheightvalue:
                self.y_data_2 = y_data
            
            self.current_target_label = None

            if self.y_data_1 is not None and self.y_data_2 is not None:
                difference = (self.y_data_1 - self.y_data_2)
                self.totdiffvalue.setText(f"{difference}")

    def save_data(self):
        if self.df is None:
            QMessageBox.warning(self, "No Data", "No CSV has been loaded.")
            return

        lat_text = self.latvalue.text()
        long_text = self.longvalue.text().replace("Longitude: ", "")
        max_height = self.maxheightvalue.text()
        min_height = self.minheightvalue.text()
        difference = self.totdiffvalue.text()

        try:
            latitude = float(lat_text)
            longitude = float(long_text)
            max_h = float(max_height)
            min_h = float(min_height)
            diff = float(difference)
        except ValueError:
            QMessageBox.warning(self, "Invalid Values", "Please make sure all values are filled in and numeric.")
            return

        save_path = "/home/lab/Documents/rutting/saved_output.csv"

        write_header = not os.path.exists(save_path)

        try:
            with open(save_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if write_header:
                    writer.writerow(["Latitude", "Longitude", "MaxHeight", "MinHeight", "Difference"])
                writer.writerow([latitude, longitude, max_h, min_h, diff])

            QMessageBox.information(self, "Saved", "Data saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save data:\n{str(e)}")

    def reset_labels(self):
        self.maximumheightbtn.setStyleSheet("""
            QPushButton {
                background-color: rgb(94, 92, 100);
            }
            QPushButton:hover {
                background-color: rgb(53, 132, 228);
            }
        """)
        self.minimumheightbtn.setStyleSheet("""
            QPushButton {
                background-color: rgb(94, 92, 100);
            }
            QPushButton:hover {
                background-color: rgb(198, 70, 0);
            }
        """)
        self.current_row = 0  
        self.first_click = None
        self.second_click = None
        self.y_data_1 = None
        self.y_data_2 = None
        self.totdiffvalue.clear()
        self.maxheightvalue.clear()
        self.minheightvalue.clear()
        self.rowinput.clear()
        
    def plot_specific_row(self):
        if self.df is not None:
            try:
                row_number = int(self.rowinput.text()) - 1  
                self.current_row = row_number
                self.rowinput.clear()
                self.get_row(self.current_row)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid row number.")

    def import_csv(self):
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )
        
        if file_path:
            try:
                
                self.df = pd.read_csv(file_path)
                
                
                self.get_row(self.current_row)
                
                
                QMessageBox.information(self, "Success", f"CSV file loaded successfully!\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file:\n{str(e)}")

    def reset_plot(self):
        if self.df is not None:
            try:
                self.reset_labels()
                self.get_row(self.current_row)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid row number.")

    def reset_all(self):
        if self.df is not None:
            try:
                self.reset_labels()
                self.reset_current_row()
            except:
                QMessageBox.warning(self, "Invalid Input", "Failed to reset to the first row.")

    def get_row(self, row_index):
        if self.df is not None and row_index < len(self.df) and row_index >= 0:
            self.rownum.setText(f"Point {row_index + 1}")
            row_data = self.df.iloc[row_index]
            latitude = row_data['gpslatitude']  
            longitude = row_data['gpslongitude']  
            self.latvalue.setText(f"{latitude}")
            self.longvalue.setText(f"{longitude}")


            fields = [f"field{i}" for i in range(450)]  
            row_data_filtered = row_data[fields]  
            self.plot_frame.plot_csv(row_data_filtered)


            try:
                if self.automate_activated is not False:
                    self.calculate_automate_markers(row_index, self.scanning_point_start, self.scanning_point_end)
            except:
                if self.y_data_1 is not None or self.y_data_2 is not None:
                    self.reset_plot()

                if row_index == 0:
                    self.setup_map(latitude, longitude)  
                else:
                    self.update_map_with_gps(latitude, longitude)
            
        else:
            QMessageBox.information(self, "End of Data", "No more rows to display.")

    def update_current_row(self):
        self.current_row += 1
        self.get_row(self.current_row)
    
    def show_previous_row(self):
        self.current_row -= 1
        self.get_row(self.current_row)

    def reset_current_row(self):
        self.current_row = 0
        self.get_row(self.current_row)
             
    def update_map_with_gps(self, latitude, longitude):
        js = f"""updateMarker({latitude}, {longitude});"""
        self.webview.page().runJavaScript(js)

    def setup_map(self, latitude, longitude):
        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Live Map</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100vh;"></div>
            <script>
                var map = L.map('map').setView([{latitude}, {longitude}], 18);
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                    name: 'Esri World Imagery'
                }}).addTo(map);

                var marker = L.marker([{latitude}, {longitude}]).addTo(map);
               
                function updateMarker(lat, lon) {{
                    marker.setLatLng([lat, lon]);
                    map.panTo([lat, lon]);
                }}
            </script>
        </body>
        </html>
        """



        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
            f.write(map_html)
            temp_file_path = f.name

        self.webview.load(QUrl.fromLocalFile(temp_file_path))

        mapwidget = self.findChild(QWidget, "mapwidget")
        if mapwidget:
            if mapwidget.layout() is None:
                layout = QVBoxLayout(mapwidget)
                mapwidget.setLayout(layout)
            mapwidget.layout().addWidget(self.webview)
        else:
            print("Error: 'mapwidget' not found.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


