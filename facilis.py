import importlib.util
from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QGroupBox, QFormLayout, QGridLayout,
                             QLabel, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QDialog, QSpinBox,
                             QFileDialog, QLineEdit, QCheckBox, QRadioButton, QPushButton,
                             QTableView, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QMessageBox, QMenuBar, QAction)

# from fbs_runtime.application_context.PyQt5 import ApplicationContext                             
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import QTimer, Qt, QSize
import subprocess
import pandas as pd
import sys
import os

# Create the PyQt5 class object for user input.
class User_Input(QWidget):
    def __init__(self):
        super(User_Input, self).__init__()
        header = ['', 'Volume Name', 'Capacity', 'Available', 'Server']

        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(5)
        self.treeWidget.setHeaderLabels(header)
        self.treeItem = QTreeWidgetItem(self.treeWidget)
        
        for index in range(0, len(volumes_df.index)):
            row = volumes_df.loc[index, :]
            item = VolumeTreeItem(self.treeWidget, row)
            
        for column in range(self.treeWidget.columnCount()):
            self.treeWidget.resizeColumnToContents(column)
            
#          ## Set Columns Width to match content:
#         for column in range( self.treeWidget.columnCount() ):
#             self.treeWidget.resizeColumnToContents( column )

        # Set our widget layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.treeWidget)
#         self.updateGeometry()
#         self.resize(self.sizeHint().width(), self.minimumHeight())
#         self.setGeometry(50, 50, 550, 200)
#         self.setFixedSize(self.layout.sizeHint())
        self.setLayout(mainLayout)       
        self.show()

    def resize_layout(self):
        self.updateGeometry()

class VolumeTreeItem(QTreeWidgetItem):
    # Custom QTreeWidgetItem with Widget
    def __init__( self, parent, row):
        
        super(VolumeTreeItem, self ).__init__( parent )
            
        # Column 0 Mount Button
        self.mount_button = QPushButton()
        self.mount_button.setText('Mount')
        self.mount_button.setCheckable(True)
#         self.mount_button.toggle()
        self.mount_button.clicked.connect(self.btnstate)
        self.treeWidget().setItemWidget(self, 0, self.mount_button)
        
        # Column 1 Volume Name
        self.setText(1, row['volume name'])
#         print(type(row['volume name']))
        
        # Column 2 Capacity
        self.setText(2, row['capacity'])
        
        # Column 3 Availablity
        self.setText(3, row['available'])
        
        # Column 4 Server Name
        self.setText(4, row['server name'])

    def btnstate(self):
        if self.mount_button.isChecked():
            self.mount_button.setText('Unmount')
        else:
            self.mount_button.setText('Mount')

if __name__ == '__main__':
#     appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    marker_app = QApplication.instance() # checks if QApplication already exists
    if not marker_app: # create QApplication if it doesnt exist
        marker_app = QApplication(sys.argv)

    ex = User_Input()
    marker_app.exec_()
#     sys.exit(marker_app.exec_())





temp_df = pd.read_csv('~/Desktop/volume_list.csv', sep = '=', header = None, index_col = False)
volume_columns = ['volume UID', 'volume name', 'server name', 'capacity', 'available']
volume_UID_col = temp_df.loc[temp_df.loc[:, 0].str.contains('volume UID')][1]
volume_name_col = temp_df.loc[temp_df.loc[:, 0].str.contains('volume name')][1]
server_name_col = temp_df.loc[temp_df.loc[:, 0].str.contains('server name')][1]
capacity_col = temp_df.loc[temp_df.loc[:, 0].str.contains('capacity')][1]
available_col = temp_df.loc[temp_df.loc[:, 0].str.contains('available')][1]
volumes_df = pd.DataFrame(columns = volume_columns)

volumes_df.loc[:, 'volume UID'] = volume_UID_col.reset_index(drop = True)
volumes_df.loc[:, 'volume name'] = volume_name_col.reset_index(drop = True)
volumes_df.loc[:, 'server name'] = server_name_col.reset_index(drop = True)
volumes_df.loc[:, 'capacity'] = capacity_col.reset_index(drop = True)
volumes_df.loc[:, 'available'] = available_col.reset_index(drop = True)