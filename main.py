import getting_a_table as gt
import some_functions as sf

people = gt.getting_a_table()
session = sf.logging() # log

sf.check_and_add(session, people)