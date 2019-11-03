import sqlite3
import random
import re
import connection as con
from datetime import date, datetime

def agent_terminal(user_info):
    print("Welcome, as a registry agent, you may perform any of the below:")
    print("1 - Register a birth")
    print("2 - Register a marriage")
    print("3 - Renew a vehicle registration")
    print("4 - Process a bill of sale")
    print("5 - Process a payment")
    print("6 - Get driver abstract")
    print("7 - log out")

    while True:
        intent = input("please type the number of the action you would like to perform")
        if intent == 1:
            register_birth(user_info)
        elif intent == 2:
            register_marriage(user_info)
        elif intent == 3:
            renew_vehicle_reg()
        elif intent == 4:
            process_bill_of_sale()
        elif intent == 5:
            process_payment()
        elif intent == 6:
            get_driver_abstract()
        elif intent == 7:
            return
        else:
            print("Invalid input")
        con.connection.commit()



def add_year(Date, years):
    # increments a given date Date by a number of years
    # Date - date to be incremented
    # years - number of years to increment date by

    try:
        # adds years to the date
        return Date.replace(year = Date.year + years)
    except ValueError:
         # if the date would be invalid after adjustment, fixes it
        return Date + (date(Date.year + years, 1, 1) - date(Date.year, 3, 1))

def get_regno():
    # Asks the user for their regno
    # returns the regno if it's valid, otherwise returns None

    userRegno = input("Provide the registration number(regno) of the registration you wish to renew: ")
    try:
        int(userRegno)
    except:
        print("Error: regno must be a number.")
        userRegno = None

    return userRegno

def query(userRegno, cur):
    # ensure the validity of the regno
    # userRegno- inputted regno
    # cur - cursor used to navigate the database

    # isValid is false when regno isnt not know to be valid, true otherwise
    isValid = False

    # query the regno
    con.c.execute("select expiry from registrations where regno = :num;", {"num":userRegno})
    res = con.c.fetchall()
    try:
        # this throws an error if the query is not as expected, ie empty or an int/str
        res[0][0]
        # if above didnt through an error, query is valid
        isValid = True
    except:
        # print error if query isnt valid
        print("Error: the entered regno is not in the database. Please enter a valid regno.")
        # ask for another regno
        userRegno = input("Provide the registration number(regno) of the registration you wish to renew: ")
    return isValid, userRegno, res

def renew_vehicle_reg():

    userRegno = None

    # get the regno
    while (userRegno == None):
        userRegno = get_regno()

    # ensure the validity of the regno
    validQuery = False
    while (validQuery == False):
        validQuery, userRegno, res = query(userRegno,con.c)

    # result is just the date from the query(takes date out of tuple)
    result = res[0][0]

    # expiry is the date from the query, turned into a date type
    expiry = datetime.date(int(result[0])*1000 + int(result[1])*100 + int(result[2])*10 + int(result[3]), int(result[5])*10 + int(result[6]), int(result[8])*10 + int(result[9]))

    # find current date
    currDate = datetime.date.today()

    if expiry <= currDate:
        # if expiry <= current date, set the new expiry date to one year from now
        newExpiry = add_year(currDate, 1)
    else:
        # otherwise, increment the expiry year by one year
        newExpiry = add_year(expiry, 1)

    # update the correct registration with the new expiry date
    con.c.execute("update registrations set expiry = :date where regno = :num;", {"date":newExpiry, "num":userRegno})

    con.c.close()



def process_bill_of_sale():
    print('Proces a Bill of Sale')

    #retrieve VIN and search for most recent registration
    vin = input("VIN of vehicle: ")
    
    con.c.execute("""
        SELECT * FROM registrations
        WHERE vin=?
        ORDER BY regdate DESC;
        """, {vin,})
    recent_reg=con.c.fetchone()

    #make sure registration exists
    if not recent_reg:
        print("VIN incorrect - not found")
        return

    #get owners name and confirm with registration
    owner_fname, owner_lname = input("Name of current owner(First Last): ").split()
    if recent_reg['fname'].lower() != owner_fname or recent_reg['lname'].lower != owner_lname:
        print("{} {} does not match most recent owner".format(owner_fname, owner_lname))
        return

    #set registration to expire today
    con.c.execute("""
    UPDATE registrations
    SET expiry = ?
    WHERE regno = ?;
    """, {date.today(), recent_reg['regno']})

    #Register new owner
    new_fname, new_lname = input("Name of new owner(First Last): ").split()
    new_plate = input("New Liscense Plate: ")
    d = date.today()
    expiry = d.replace(year=d.year + 1)
    regno = new_primary_key('registrations', 'regno')

    con.c.execute("""
    INSERT INTO registrations
    VALUES(:regno, :regdate, :expiry, :plate, :vin, :fname, :lname);
    """, {'regno': regno, 'regdate': d, 'expiry': expiry, 'plate': new_plate, 'vin':  recent_reg['vin'], 'fname': new_fname, 'lname': new_lname})

    con.connection.commit()

    print("Bill of Sale Successfully Processed")
    return



def get_driver_abstract():
    print("Get Driver Abstract")

    fname, lname = input("Driver's name(First Last): ")

    #get driver ticket info
    con.c.execute("""
    SELECT fname, lname, COUNT(tno) as tickets
    FROM registrations r, tickets t
    WHERE r.regno = t.regno
    AND fname = ? COLLATE NOCASE
    AND lname = ? COLLATE NOCASE;
    """, {fname, lname})

    tickets = con.c.fetchone()['tickets']

    #get number of demerit notices, get demerits within 2 yrs and lifetime demerits
    con.c.execute("""
    TODO
    """)

    if tickets == 0:
        return
    
    see_tickets = input("Would you like to view tickets recieved (y/n)?: ")
    if see_tickets.lower() != 'y':
        return


    offset = 0
    while see_tickets.lower() == 'y':
        #get info about tickets
        con.c.execute("""
        SELECT tno, vdate, fine, r.regno, make, model, violation
        FROM registrations r, tickets t, vehicles v
        WHERE r.regno = t.regno
        AND r.vin = v.vin
        AND fname = ? COLLATE NOCASE
        AND lname = ? COLLATE NOCASE
        ORDER BY vdate DESC
        LIMIT 5 OFFSET ?;
        """, {fname, lname, offset})
        rows = con.c.fetchall()
        offset += 5

        if not rows:
            print("All tickets have been displayed")
            return
        
        for row in rows:
            print(row)

        if len(rows) == 5:
            see_tickets = input("Would like like to view more (y/n)?")
        else:
            see_tickets = 'n'

    return



def new_primary_key(table, primary_key):
    con.c.execute("""
    SELECT Max(?)
    FROM ?;
    """, {primary_key, table})

    return int(con.c.fetchone()) + 1



def register_birth(user_info):

    #city_of_user =user[5]
        
 
        #Generate new unique birth number by looping until unique
        def exe_register_birth():
            try:
                unique=False
                while not unique:
                    generated_birthregno = random.randint(1,1001)
                    con.c.execute("""SELECT regno from births WHERE regno=:generated_birthregno  """,{'generated_birthregno':generated_birthregno})
                    
                    if con.c.fetchone() == None:
                        unique=True
                
                valid_entry,mfname,mlname,ffname,flname=secure_name_input()
                con.connection.commit()
                
                mother_registered,mother_info=is_parent_in_register(mfname,mlname)
                father_registered,father_info=is_parent_in_register(ffname,flname)
                mfname=mother_info[0]
                mlname=mother_info[1]
                ffname=father_info[0]
                flname=father_info[1]
                
                if not mother_registered:
                    add_parent(mfname,mlname)
                if not father_registered:
                    add_parent(ffname,flname)
                
                con.c.execute("""SELECT address, phone FROM persons WHERE UPPER(fname)=:mfname AND UPPER(lname)=:mlname""", {'mfname':mfname.upper(), 'mlname':mlname.upper()} )
                mother_info=con.c.fetchone()
                
                mother_address=mother_info[0]
                mother_phone=mother_info[1]
                user_bplace=user_info[5]

                
                add_child(generated_birthregno,user_bplace,mfname,mlname,ffname,flname,mother_address,mother_phone)
                con.connection.commit()
                print("Birth registered sucessfully")
            except sqlite3.OperationalError as e:
                if "locked" in e.args[0]:
                    print("The database seem to be locked please close all concurrent acceses in your computer")
                else:
                     print("An unexpected error has ocurred please retry")
                     print(e.args)

            
        #Ask for the parents first name and last name
        
        def secure_name_input():
            valid_entry=False
            while (not valid_entry):
                
                mfname=input("Please input the mother's first name ")
                mlname=input("Please input the mother's last name ")
                
                if not re.match("^[A-Za-z0-9_ ]*$", mfname) or not re.match("^[A-Za-z0-9_ ]*$", mlname):
                    print("the input for mother is not valid, do not use special characters")
                    YN= input("Do you want to try again? (Y/N) ")
                    if YN == 'N':
                        return None,None,None,None,None
                else:
                    valid_father_entry = False
                    while not valid_father_entry:
                        ffname=input("Please input the fathers first name ")
                        flname=input("Please input the fathers last name ")
                        
                        if re.match("^[A-Za-z0-9_ ]*$", ffname) and re.match("^[A-Za-z0-9_ ]*$", flname):
                            valid_father_entry = True
                            valid_entry = True
                            return True,mfname,mlname,ffname,flname
                            
                        else:
                            print("The input for the father is not valid, do not use special charaters")
                            YN = input("Do you want to try again? (Y/N)")
                            if YN == 'N':
                                return None,None,None,None

        def is_parent_in_register(pfname,plname):


            con.c.execute(""" SELECT * FROM persons WHERE UPPER(fname)=:pfname AND UPPER(lname)=:plname """, {'pfname':pfname.upper(), 'plname':plname.upper()})
            con.connection.commit()
            parent_info = con.c.fetchone()
            if parent_info != None:
                return True,parent_info
            else:
                return False,[pfname,plname]
            

        def add_parent(fname,lname):

            txt=('Please input the birth date of %s %s in the format YYYY-MM-DD ' %(fname,lname))
            safe_bdate_format = False
            
            
            #input bdate
            while safe_bdate_format == False:
                try:
                    bdate_input = input(txt)
                    bdate = datetime.strptime(bdate_input, '%Y-%m-%d')
                    safe_bdate_format=True      
                    bdate = str(bdate).split()[0]
                    
                except ValueError:
                    if len(bdate_input) == 0 or str(bdate_input).upper() =='NULL' or str(bdate_input).upper() == 'NONE' :
                        bdate_input = None
                        safe_bdate_format=True
                    else:
                        print('the format is incorrect format')  
            
            
            #input address
            
            safe_address_format = False
             
            while safe_address_format == False:
                txt=("Please input %s %s's address " %(fname,lname))
                address_input=input(txt)
                if re.match("^[A-Za-z0-9_ ]*$", address_input):
                    safe_address_format = True
                else:
                    print('Invalid input do not use special characters')
            if len(address_input) == 0 or str(address_input).upper() =='NONE' or str(address_input).upper()=='NULL':
                address_input = None
              
            #input phone number
            
            safe_phone_format = False
            
            while safe_phone_format == False:
                txt=("Please input %s %s' phone number " %(fname,lname))
                phone_input=input(txt)
                if re.match("^[A-Za-z0-9_ -]*$", phone_input):
                    safe_phone_format = True
                else:
                    print('Invalid input do not use special characters other than hyphen')
            if len(phone_input) == 0 or str(bdate_input).upper() == 'NONE':
                phone_input=None 
                
            #input bpalce
            safe_bplace_format = False
             
            while safe_bplace_format == False:
                txt=("Please input %s %s's birthplace " %(fname,lname))
                bplace_input=input(txt)
                if re.match("^[A-Za-z0-9_, ]*$", bplace_input):
                    safe_bplace_format = True
                else:
                    print('Invalid input do not use special characters')
            if len(bplace_input) == 0 or str(bplace_input).upper() == 'NULL':
                bplace_input=None
                
            
            con.c.execute(""" INSERT INTO persons VALUES (:fname,:lname,:bdate,:bplace,:address,:phone)""", {'fname':fname,'lname':lname,'bplace':bplace_input,'bdate':bdate_input,'address':address_input,'phone':phone_input})
            con.connection.commit() 
           
            
            
        def add_child(generated_birthregno,user_bplace,mfname,mlname,ffname,flname,mother_address,mother_phone):
            not_unique_name = True
            today = date.today().strftime("%Y-%m-%d")
            
            safe_gender_format = False 
            
            while not_unique_name == True:
               
                    safe_child_name = False
                    
                    while safe_child_name == False:
                        cfname=input("Please input the child first name ")
                        clname=input("Please input the child last name ")
                        if re.match("^[A-Za-z0-9_ ]*$", cfname) and re.match("^[A-Za-z0-9_ ]*$", clname):
                            safe_child_name=True
                        else:
                            print("Invalid input do not use special characters")
                            
                    con.c.execute("""SELECT fname, lname FROM persons where UPPER(fname)=:cfname AND UPPER(lname)=:clname """, {'cfname':cfname.upper(), 'clname':clname.upper()})
                
                    
                    if con.c.fetchone() == None:
                        not_unique_name = False
                        print("The combination of first and last name has to be unique please change the either")
            
            
            
            safe_gender_format = False
            while safe_gender_format == False:
                gender=input("Please enter the child's gender (M/F) ")
                if gender.upper() != 'M' and gender.upper() != 'F':
                    print("Invalid input please enter only either M or F")
                else:
                    safe_gender_format = True
                        
            con.c.execute(""" INSERT INTO persons values (:fname,:lname,:bdate,:bplace,:address,:phone) """,{'fname':cfname,'lname':clname,'bdate':today, 'bplace':user_bplace,'address':mother_address,'phone':mother_phone})
            con.connection.commit()
            con.c.execute(""" INSERT INTO births values (:regno,:fname,:lname,:regdate,:regplace,:gender,:f_fname,:f_lname,:m_fname,:m_lname)""",{'regno':generated_birthregno,'fname':cfname,'lname':clname,'regplace':user_bplace,'regdate':today,'gender':gender.upper(),'f_fname':ffname,'f_lname':flname,'m_fname':mfname,'m_lname':mlname})
            
            con.connection.commit()
           
            

        exe_register_birth()

        
        


def register_marriage(user_info):
    
    def exe_register_marriage():
            try:
                unique=False
                while not unique:
                    generated_marriageregno = random.randint(1,1001)
                    con.c.execute("""SELECT regno from births WHERE regno=:generated_birthregno  """,{'generated_birthregno':generated_marriageregno})
                    
                    if con.c.fetchone() == None:
                        unique=True
                valid_entry,p1fname,p1lname,p2fname,p2lname=secure_name_input()
                con.connection.commit()
                
                p1_registered,p1_info=is_partner_in_register(p1fname,p1lname)
                p2_registered,p2_info=is_partner_in_register(p2fname,p2lname)
                
                
                if not p1_registered:
                    add_partner(p1fname,p1lname)
                if not p2_registered:
                    add_partner(p2fname,p2lname)
                
                user_bplace=user_info[5]
                
                add_marriage(generated_marriageregno,user_bplace,p1_info[0],p1_info[1],p2_info[0],p2_info[1])
                print("Marriage registered Succesfully")
            except sqlite3.Error as e:
                if "locked" in e.args[0]:
                    print("The database seem to be locked please close all concurrent acceses in your computer")

                else:
                     print("An unexpected error has ocurred please retry")
                     print(e.args)
                
        
    
    def secure_name_input():
            valid_entry=False
            while (not valid_entry):
                print(valid_entry)
                p1fname=input("Please input the 1st partner's first name ")
                p1lname=input("Please input the 1st partner's last name ")
                
                if not re.match("^[A-Za-z0-9_ ]*$", p1fname) or not re.match("^[A-Za-z0-9_ ]*$", p1lname):
                    print("the input for the 1st partner is not valid, do not use special characters")
                    YN= input("Do you want to try again? (Y/N) ")
                    if YN == 'N':
                        return None,None,None,None,None
                else:
                    valid_father_entry = False
                    while not valid_father_entry:
                        p2fname=input("Please input the 2nd partner's first name ")
                        p2lname=input("Please input the 2nd partner's last name ")
                        
                        if re.match("^[A-Za-z0-9_ ]*$", p2fname) and re.match("^[A-Za-z0-9_ ]*$", p2lname):
                            valid_father_entry = True
                            valid_entry = True
                            return True,p1fname,p1lname,p2fname,p2lname
                            
                        else:
                            print("The input for the father is not valid, do not use special charaters")
                            YN = input("Do you want to try again? (Y/N)")
                            if YN == 'N':
                                return None,None,None,None        
        
        
    def is_partner_in_register(pfname,plname):
            con.c.execute(""" SELECT * FROM persons WHERE UPPER(fname)=:pfname AND UPPER(lname)=:plname """, {'pfname':pfname.upper(), 'plname':plname.upper()})
            con.connection.commit()
            partner_info = con.c.fetchone()
            if partner_info != None:
                return True,partner_info
            else:
                return False,[pfname,plname]
      
    
    def add_partner(fname,lname):
            txt=('Please input the birth date of %s %s in the format YYYY-MM-DD ' %(fname,lname))
            safe_bdate_format = False
            
            
            #input bdate
            while safe_bdate_format == False:
                try:
                    bdate_input = input(txt)
                    bdate = datetime.strptime(bdate_input, '%Y-%m-%d')
                    safe_bdate_format=True      
                    bdate = str(bdate).split()[0]
                    
                except ValueError:
                    if len(bdate_input) == 0 or str(bdate_input).upper() =='NULL' or str(bdate_input).upper() == 'NONE' :
                        bdate_input = None
                        safe_bdate_format=True
                    else:
                        print('the format is incorrect format')  
            
            
            #input address
            
            safe_address_format = False
             
            while safe_address_format == False:
                txt=("Please input %s %s's address " %(fname,lname))
                address_input=input(txt)
                if re.match("^[A-Za-z0-9_ ]*$", address_input):
                    safe_address_format = True
                else:
                    print('Invalid input do not use special characters')
            if len(address_input) == 0 or str(address_input).upper() =='NONE' or str(address_input).upper()=='NULL':
                address_input = None
              
            #input phone number
            
            safe_phone_format = False
            
            while safe_phone_format == False:
                txt=("Please input %s %s' phone number " %(fname,lname))
                phone_input=input(txt)
                if re.match("^[A-Za-z0-9_ -]*$", phone_input):
                    safe_phone_format = True
                else:
                    print('Invalid input do not use special characters other than hyphen')
            if len(phone_input) == 0 or str(bdate_input).upper() == 'NONE':
                phone_input=None 
                
            #input bpalce
            safe_bplace_format = False
             
            while safe_bplace_format == False:
                txt=("Please input %s %s's birthplace " %(fname,lname))
                bplace_input=input(txt)
                if re.match("^[A-Za-z0-9_, ]*$", bplace_input):
                    safe_bplace_format = True
                else:
                    print('Invalid input do not use special characters')
            if len(bplace_input) == 0 or str(bplace_input).upper() == 'NULL':
                bplace_input=None
                
            
            con.c.execute(""" INSERT INTO persons VALUES (:fname,:lname,:bdate,:bplace,:address,:phone)""", {'fname':fname,'lname':lname,'bplace':bplace_input,'bdate':bdate_input,'address':address_input,'phone':phone_input})
            con.connection.commit() 
            return fname,lname
    def add_marriage(generated_marriageregno,user_bplace,p1fname,p1lname,p2fname,p2lname):
            today = date.today().strftime("%Y-%m-%d")
            con.c.execute(""" INSERT INTO marriages values (:regno,:regdate,:regplace,:p1_fname,:p1_lname,:p2_fname,:p2_lname)""",{'regno':generated_marriageregno,'regdate':today,'regplace':user_bplace,'p1_fname':p1fname,'p1_lname':p1lname,'p2_fname':p2fname,'p2_lname':p2lname})
            con.connection.commit()
            
    exe_register_marriage()