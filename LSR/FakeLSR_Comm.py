import random
import time


class FakeLSR_comm:

    def __init__(self):
        self.columns_with_data = []
        self.column_1 = []
        self.temp = -1
        time.sleep(0.5)

    def send_any_command(self, msg):
        print("Sent: ",bytes(msg, 'utf-8'))
        time.sleep(0.005)

        print("\t LSR reponsed: ")

    def ask_for_status(self):
        msg = "{\"DO\":\"status\"}"
        self.temp = random.randint(20,28)
        self.send_any_command(msg)

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
        self.send_any_command(msg)

    def run(self):
        if 1 in self.columns_with_data and 2 in self.columns_with_data and 3 in self.columns_with_data and 4 in self.columns_with_data:
            msg = "{\"DO\": \"run\"}"
            self.send_any_command(msg)
            self.columns_with_data = []
        else:
            print("\t ERROR: All column values should be set first")

    def stop(self):
        msg = "{\"DO\": \"stop\"}"
        self.send_any_command(msg)

