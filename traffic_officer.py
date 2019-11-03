import sqlite3
import connection as con
import random
import re
from datetime import date, datetime

def officer_terminal():
    print("Welcome, as a traffic officer you are able to perform the following actions")
    print("1 - Issue a ticket")
    print("2 - Find a car owner")
    print("3 - Log out")

    while True:
        intent = input("please type the number of the action you would like to perform: ")
        try:
            int(intent)
        except:
            pass

        if intent == 1:
            issue_a_ticket()
        elif intent == 2:
            find_car_owner()
        elif intent == 3:
            return
        else:
            print("Invalid input")
        con.connection.commit()


def issue_a_ticket():
    def exe_issue_a_ticket():
        try:
            today = date.today().strftime("%Y-%m-%d")
            
            unique = False
            while not unique:
                generated_tno = random.randint(1,1001)
                con.c.execute("""SELECT tno from tickets WHERE regno=:generated_tno  """,{'generated_tno':generated_tno})
                if con.c.fetchone() == None:
                    unique=True
                    
            
            regno=validate_regno()
            
            con.c.execute("""SELECT r.regno,r.fname, r.lname,v.vin,v.model,v.color, v.make,v.year FROM registrations r, vehicles v WHERE r.vin=v.vin AND r.regno=:regno""",{'regno':regno})
            offender_info = con.c.fetchone()
            print('regno: ',offender_info[0],' name: ',offender_info[1], ' ',offender_info[2], ' vin: ',offender_info[3],
            ' model :',offender_info[4], ' color: ', offender_info[5], ' make: ', offender_info[6], ' year: ', offender_info[7])
            
            safe_description_format = False
            while safe_description_format == False:
                description=input('Please describe the violation, do not use special characters ')
                
                if re.match("^[A-Za-z0-9_ -]*$", description):
                    safe_description_format = True
                else:
                    print('Invalid input do not use special characters')
            
            
            safe_fine_format = False
            
            while safe_fine_format == False:
                fine=input('Please enter the fine amount, input numbers only ')
                
                if re.match("^[0-9 ]*$", fine):
                    safe_fine_format = True
                else:
                    print('Invalid input do not use special characters')
                    
            enter_date=input("Was the infraction today? (Y/N) ")
            
            if enter_date == 'N':
                txt=('Please input the date of the violation in the format YYYY-MM-DD ')
                safe_bdate_format = False
            
            
            #input bdate
                while safe_bdate_format == False:
                    try:
                        bdate_input = input(txt)
                        bdate = datetime.strptime(bdate_input, '%Y-%m-%d')
                        safe_bdate_format=True      
                        today = str(bdate).split()[0]
                        
                    except ValueError:
                        if len(bdate_input) == 0 or str(bdate_input).upper() =='NULL' or str(bdate_input).upper() == 'NONE' :
                            bdate_input = None
                            safe_bdate_format=True
                        else:
                            print('the format is incorrect format retry')                  
                
            con.c.execute(""" INSERT INTO tickets values (:tno,:regno,:fine,:violation,:vdate)""",{'tno':generated_tno,'regno':regno,'fine':fine,'violation':description,'vdate':today})
            print("Ticket registered succesfully")

        
        except sqlite3.OperationalError as e:
                #if "locked" in e.args[0]:
                    print("The database seem to be locked please close all concurrent acceses in your computer")
                    print(e.args[0])
                    con.connection.close()
                
       
    def validate_regno():
        safe_regno_format = False
        regno_is_real = False
             
        while safe_regno_format == False:
            txt=("Please input the offender's regno ")
            regno_input=input(txt)
            while regno_is_real == False and re.match("^[0-9]*$", regno_input):
                    con.c.execute(""" SELECT regno FROM registrations WHERE regno=:regno_input""",{'regno_input':regno_input})
                    regno_info=con.c.fetchone()                     
                    if regno_info != None:                          #if the result is not empty ends the while loop                                       
                        regno_is_real = True
                        return regno_input
                    else:
                        print("The input does not correspond to any existent regno, please entery a valid regno")
                        break
                    
            else:
                print('the regno input should consist of numbers only')
        

        
    exe_issue_a_ticket()    

def find_car_owner():
    pass