# https://forbiz-online.org/kak-iz-python-podklyuchitsya-k-google-sheet/

import gspread
import config as cf

def getting_a_table():
    gs = gspread.service_account(filename='credits_for_a_table.json')  # add credits_for_a_table.json
    sh = gs.open_by_key(cf.TABLE_KEY)  # open the table by ID
    worksheet = sh.sheet1  # get the 1st sheet

    res = worksheet.get_all_values()
    # print(res)
    # elem = worksheet.get('A2')
    # print(elem)
    return res