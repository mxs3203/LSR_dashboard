import time

import serial

class LSR_comm:

    def __init__(self, com_port):
        self.S = serial.Serial(com_port, timeout=.1, baudrate=1000000)
        self.columns_with_data = []
        self.column_1 = []
        self.set_temp = -1
        self.block_temp = -1
        self.current_process = ""
        self.tec_status = ""
        time.sleep(0.5)

    def send_any_command(self, msg):
        print("\tSent: ",bytes(msg, 'utf-8'))
        self.S.write(bytes(msg, 'utf-8'))
        time.sleep(0.005)
        response = self.S.readlines()
        print("\t LSR reponsed: ", response)
        return response

    def ask_for_status(self):
        msg = "{\"DO\":\"status\"}"
        self.parseStatus(self.send_any_command(msg))

    def parseStatus(self, responseFromLSR):
        self.current_process = responseFromLSR[1].decode("utf-8").split(":")[1].strip()
        self.tec_status = responseFromLSR[2].decode("utf-8").split(":")[1].strip()
        self.set_temp = responseFromLSR[3].decode("utf-8").split("=")[1].strip()
        self.block_temp = responseFromLSR[4].decode("utf-8").split("=")[1].strip()
        print(self.current_process, self.tec_status, self.set_temp, self.block_temp)

    def set_column_data(self, column, list_of_nums, coef=1):

        if len(list_of_nums) == 10:
            if column == 1:
                list_of_nums = [item * coef for item in list_of_nums]
                self.column_1 = list_of_nums
            msg = "{\"DATA\":{" + "\"Col-{}\": [{},{},{},{},{},{},{},{},{},{}]".format(column,list_of_nums[0],list_of_nums[1],
                                                                                       list_of_nums[2],
                                                                     list_of_nums[3],list_of_nums[4], list_of_nums[5],
                                                                     list_of_nums[6],list_of_nums[7],list_of_nums[8],
                                                                     list_of_nums[9]) + "}}"
            self.send_any_command(msg)
            self.columns_with_data.append(column)
        else:
            print("\t List should contain exactly 10 numbers")
        time.sleep(0.01)

    # Generate second,third or fourth column based on values of first column (75%,50% and 30% intesity)
    def compute_column_based_on_first(self, coef):
        col_vals = []
        if 1 in self.columns_with_data:
            for i in self.column_1:
                col_vals.append(int(i * coef))

        return col_vals

    def set_block_temp(self, temp):
        msg  = "{\"DATA\":{" + "\"Tblock\": {}".format(temp) + "}}"
        print(msg)
        self.send_any_command(msg)

    def run(self):
        if (self.block_temp != -1) or (1 in self.columns_with_data and 2 in self.columns_with_data and 3 in self.columns_with_data and 4 in self.columns_with_data):
            msg = "{\"DO\": \"run\"}"
            self.send_any_command(msg)
            self.columns_with_data = []
        else:
            print("\t ERROR: All column values should be set first")

    def stop(self):
        msg = "{\"DO\": \"stop\"}"
        self.send_any_command(msg)
