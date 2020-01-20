import importlib.util
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QDialog, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QMenuBar, QAction)

# from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

import subprocess
import pandas as pd
import sys
import os

# Function to run mount/unmount commands to our Terrablocks for given volume.
def terrablock_commands(command, server_name, volume_name):
    volume_name = volume_name
    server_name = server_name
    volume_path = '/media/' + volume_name
    tb_command = 0
    if(command == 'mount'):
        if os.path.exists(volume_path):
            if not os.listdir(volume_path):
                #tb_command = os.system(f'factbcmd legacy_fc_mount {server_name} {volume_name}')
                print(f'factbcmd legacy_fc_mount {server_name} {volume_name}')
            else:
                return False
        else:
            #tb_command = os.system(f'factbcmd legacy_fc_mount {server_name} {volume_name}')
            print(f'factbcmd legacy_fc_mount {server_name} {volume_name}')
    elif(command == 'unmount'):
        #tb_command = os.system(f'factbcmd legacy_fc_unmount {volume_name}')
        print(f'factbcmd legacy_fc_unmount {volume_name}')

    if tb_command == 0:
        return True
    else:
        return False

# Function to get updated list of Terrablock volumes.
def terrablock_get_list():
    # Create out data frame with our headers
    volume_columns = ['volume UID', 'volume name', 'server name', 'capacity', 'available']
    volumes_df = pd.DataFrame(columns=volume_columns)

    # Export the latest list of volumes from our Terrablocks.  Import into a panda and delete the volume list file.
    #os.system('factbcmd list_volumes > /tmp/volume_list.txt')
    #temp_df = pd.read_csv('/tmp/volume_list.txt', sep = '=', header = None, index_col = False)
    temp_df = pd.read_csv('/Users/schang/Desktop/volume_list.txt', sep='=', header=None, index_col=False)
    #os.system('rm /tmp/volume_list.txt')

    # Create temp arrays for each item we need.
    volume_UID_col = temp_df.loc[temp_df.loc[:, 0].str.contains('volume UID')][1]
    volume_name_col = temp_df.loc[temp_df.loc[:, 0].str.contains('volume name')][1]
    server_name_col = temp_df.loc[temp_df.loc[:, 0].str.contains('server name')][1]
    capacity_col = temp_df.loc[temp_df.loc[:, 0].str.contains('capacity')][1]
    available_col = temp_df.loc[temp_df.loc[:, 0].str.contains('available')][1]

    # Populate our data frame with information.
    volumes_df.loc[:, 'volume UID'] = volume_UID_col.reset_index(drop=True).str.lstrip()
    volumes_df.loc[:, 'volume name'] = volume_name_col.reset_index(drop=True).str.lstrip()
    volumes_df.loc[:, 'server name'] = server_name_col.reset_index(drop=True).str.lstrip()
    volumes_df.loc[:, 'capacity'] = capacity_col.reset_index(drop=True).str.lstrip()
    volumes_df.loc[:, 'available'] = available_col.reset_index(drop=True).str.lstrip()

    # Sort our data frame by volume name.
    volumes_df.sort_values(['volume name'], inplace=True)
    volumes_df.reset_index(drop=True, inplace=True)

    return volumes_df

class User_Input(QWidget):
    def __init__(self):
        super(User_Input, self).__init__()
        self.title = 'Facilis Terrablock Volumes'
        self.left = 0
        self.top = 0
        self.width = 530
        self.height = 500
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.create_table()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)

        refresh_action = QAction('Refresh', self)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.triggered.connect(self.refresh_list)
        quit_action = QAction('Close', self)
        quit_action.setShortcut('Ctrl+C')
        quit_action.triggered.connect(self.close)

        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)
        self.layout.addWidget(menu_bar)

        self.show()

    def create_table(self):
        header = ['', 'Volume Name', 'Capacity', 'Available', 'Server']
        volumes_df = terrablock_get_list()
        self.current_volume_uids = []
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(volumes_df.index))
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(header)
        self.table_widget.verticalHeader().setVisible(False)

        for index in range(0, len(volumes_df.index)):
            row = volumes_df.loc[index, :]
            self.current_volume_uids.append(row['volume UID'])
            self.create_row(index, row)

        for column in range(0, self.table_widget.columnCount()):
            self.table_widget.resizeColumnToContents(column)
        self.table_widget.setSortingEnabled(True)

        self.og_bg_color = self.table_widget.item(1, 1).background()

    def on_click(self):
        button = self.sender()
        if button:
            row = self.table_widget.indexAt(button.pos()).row()
        volume_name = self.table_widget.item(row, 1).text()
        server_name = self.table_widget.item(row, 4).text()
        if button.isChecked():
            command = 'mount'
            if(terrablock_commands(command, server_name, volume_name)):
                button.setText('Unmount')
                for col in range(1, 5):
                    self.table_widget.item(row, col).setBackground(QColor(0, 0, 255, 35))
            else:
                button.setChecked(False)
                self.popup_error(volume_name)
        else:
            command = 'unmount'
            if(terrablock_commands(command, server_name, volume_name)):
                button.setText('Mount')
                for col in range(1, 5):
                    self.table_widget.item(row, col).setBackground(self.og_bg_color)

    def create_row(self, index, row):

        # Column 0 Mount Button
        self.mount_button = QPushButton()
        self.mount_button.setMinimumWidth(90)
        self.mount_button.setMaximumWidth(90)
        self.mount_button.setText('Mount')
        self.mount_button.setCheckable(True)
        self.mount_button.clicked.connect(self.on_click)
        self.table_widget.setCellWidget(index, 0, self.mount_button)

        # Column 1 Volume Name
        self.volume_item = QTableWidgetItem(row['volume name'])
        self.volume_item.setFlags(Qt.ItemIsEnabled)
        self.table_widget.setItem(index, 1, self.volume_item)

        # Column 2 Capacity
        self.capacity_item = QTableWidgetItem(row['capacity'])
        self.capacity_item.setFlags(Qt.ItemIsEnabled)
        self.table_widget.setItem(index, 2, self.capacity_item)

        # Column 3 Availablity
        self.availablity_item = QTableWidgetItem(row['available'])
        self.availablity_item.setFlags(Qt.ItemIsEnabled)
        self.table_widget.setItem(index, 3, self.availablity_item)

        # Column 4 Server Name
        self.server_item = QTableWidgetItem(row['server name'])
        self.server_item.setFlags(Qt.ItemIsEnabled)
        self.table_widget.setItem(index, 4, self.server_item)

        # Column 5 Volume UID, hidden from user
        self.vuid_item = QTableWidgetItem(row['volume UID'])
        self.table_widget.setItem(index, 5, self.vuid_item)
        self.table_widget.setColumnHidden(5, True)

    def delete_row(self, volume_uid):
        row = self.table_widget.findItems(volume_uid, Qt.MatchExactly)[0].row()
        server_name = self.table_widget.item(row, 4).text()
        volume_name = self.table_widget.item(row, 1).text()
        if terrablock_commands('unmount', server_name, volume_name):
            self.table_widget.removeRow(row)
        else:
            QMessageBox.about(
                self, 'Error', f'Could not remove {volume_name}, volume is in use.  Please unmount.')

    def refresh_list(self):
        self.table_widget.setSortingEnabled(False)

        new_volumes_df = terrablock_get_list()
        new_volume_uids = []

        for index in range(0, len(new_volumes_df.index)):
            row = new_volumes_df.loc[index, :]
            new_volume_uids.append(row['volume UID'])

        volumes_added = list(set(new_volume_uids) -
                             set(self.current_volume_uids))
        volumes_removed = list(
            set(self.current_volume_uids) - set(new_volume_uids))
        volumes_updated = list(set(new_volume_uids) &
                               set(self.current_volume_uids))

        for updated_volume in volumes_updated:
            row = self.table_widget.findItems(updated_volume, Qt.MatchExactly)[0].row()
            updated_info = new_volumes_df[new_volumes_df.loc[:, 'volume UID'] == updated_volume]
            updated_info = updated_info.iloc[0]  # Turn into Panda Series

            # Column 1 Volume Name update
            if self.table_widget.item(row, 1).text() != updated_info['volume name']:
                current_item_color = self.table_widget.item(row, 1).background()
                self.volume_item = QTableWidgetItem(updated_info['volume name'])
                self.volume_item.setFlags(Qt.ItemIsEnabled)
                self.table_widget.setItem(row, 1, self.volume_item)
                self.table_widget.item(row, 1).setBackground(current_item_color)

            # Column 2 Capacity
            if self.table_widget.item(row, 2).text() != updated_info['capacity']:
                current_item_color = self.table_widget.item(row, 2).background()
                self.capacity_item = QTableWidgetItem(updated_info['capacity'])
                self.capacity_item.setFlags(Qt.ItemIsEnabled)
                self.table_widget.setItem(row, 2, self.capacity_item)
                self.table_widget.item(row, 2).setBackground(current_item_color)

            # Column 3 Availablity
            if self.table_widget.item(row, 3).text() != updated_info['available']:
                current_item_color = self.table_widget.item(row, 3).background()
                self.availablity_item = QTableWidgetItem(updated_info['available'])
                self.availablity_item.setFlags(Qt.ItemIsEnabled)
                self.table_widget.setItem(row, 3, self.availablity_item)
                self.table_widget.item(row, 3).setBackground(current_item_color)

            # Column 4 Server Name
            if self.table_widget.item(row, 4).text() != updated_info['server name']:
                current_item_color = self.table_widget.item(row, 4).background()
                self.server_item = QTableWidgetItem(updated_info['server name'])
                self.server_item.setFlags(Qt.ItemIsEnabled)
                self.table_widget.setItem(row, 4, self.server_item)
                self.table_widget.item(row, 4).setBackground(current_item_color)

        # Add any new volumes
        for added_volume in volumes_added:
            row_num = self.table_widget.rowCount()
            add_row = new_volumes_df[new_volumes_df.loc[:, 'volume UID'] == added_volume]
            add_row = add_row.iloc[0]
            self.table_widget.setRowCount(row_num + 1)
            self.create_row(row_num, add_row)

        # Remove all volumes that are no longer accessible
        for removed_volume in volumes_removed:
            self.delete_row(removed_volume)

        self.current_volume_uids = new_volume_uids

        self.table_widget.setSortingEnabled(True)

    def popup_error(self, volume_name):
        volume_name = volume_name.strip()
        file_path = '/media/' + volume_name + '/'
        QMessageBox.about(self, 'Error', f'Could not mount {volume_name}.  Please check to make sure {file_path} is empty.')

if __name__ == '__main__':
#     appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    terrablock_app = QApplication.instance() # checks if QApplication already exists
    if not terrablock_app: # create QApplication if it doesnt exist
        terrablock_app = QApplication(sys.argv)

    ex = User_Input()
    terrablock_app.exec_()
#     sys.exit(terrablock_app.exec_())