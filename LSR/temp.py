import time

from LSR.LSR_comm import LSR_comm

lsr = LSR_comm("COM3")
# lsr.set_column_data(1, [0 ] *10)
# lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
# # lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
# lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
lsr.set_block_temp(220)
#lsr.run()

while(True):
    lsr.ask_for_status()
    time.sleep(2)