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

        if intent == '1':
            issue_a_ticket()
        elif intent == '2':
            find_car_owner()
        elif intent == '3':
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
    c = con.cursor()

    # get the inputs from user about the car information    
    make = input("Provide the make of a car to search for(or press enter to search for the model): ")
    model = input("Provide the model of a car to search for(or press enter to search for the year): ")
    year = input("Provide the year of the car you want to search for(or press enter to search for the color): ")
    color = input("Provide the color of the car you want to search for(or press enter to search for the plate): ")
    plate = input("Provide the plate of the car you want to search for(or press enter to perform the search): ")

    # make empty tuples with respect to the potentially inputted informations
    makeTup = ()
    modelTup = ()
    yearTup = ()
    colorTup = ()
    plateTup = ()

    # if there are any inputs in a given piece of information, query the vin for those inputs
    if (len(make) > 1):
        c.execute("select vin from vehicles where make = :make collate NOCASE;", {"make":make})
        makeTup = c.fetchall()

    if (len(model) > 1):
        c.execute("select vin from vehicles where model = :model collate NOCASE;", {"model":model})
        modelTup = c.fetchall()

    if (len(year) > 1):
        c.execute("select vin from vehicles where year = :year collate NOCASE;", {"year":year})
        yearTup = c.fetchall()

    if (len(color) > 1):
        c.execute("select vin from vehicles where color = :color collate NOCASE;", {"color":color})
        colorTup = c.fetchall()

    if (len(plate) > 1):
        c.execute("select vin from registrations where plate = :plate collate NOCASE", {"plate":plate})
        plateTup = c.fetchall()

    # carSet holds all the vin
    carSet = set()

    # store the previously found vins in carSet
    if (len(makeTup) > 0):
        for car in range(len(makeTup)):
            carSet.add(makeTup[car][0])

    if (len(modelTup) > 0):
        for car in range(len(modelTup)):
            carSet.add(modelTup[car][0])

    if (len(yearTup) > 0):
        for car in range(len(yearTup)):
            carSet.add(yearTup[car][0])

    if (len(colorTup) > 0):
        for car in range(len(colorTup)):
            carSet.add(colorTup[car][0])

    if (len(plateTup) > 0):
        for car in range(len(plateTup)):
            carSet.add(plateTup[car][0])

    # returns if nothing was inputted
    if (len(carSet) == 0):
        print("There was not any input or no values were returned. Returning...")
        return


    # if there were inputes
    if (len(carSet) > 0):
        # infoList will hold the desired information with respect to the cars the user wants to know more about
        infoList = list()
        # for each vin, find the necessary information
        for vin in carSet:
            # tempList temporarily holds the queried info
            tempList = list()

            # find all desired information from the vehicles table
            c.execute("select make, model, year, color from vehicles where vin = :vin;", {"vin":vin})
            temp = c.fetchall()
            # append all acquired information to the temporary list
            for info in range(len(temp)):
                tempList.append(temp[info])

            # find all the desired information from the registrations table
            c.execute("select plate, regdate, expiry, fname, lname from registrations where vin = :vin;",   {"vin":vin})
            temp = c.fetchall()
            # append all acquired information to the temporary list
            for info in range(len(temp)):
                tempList.append(temp[info])

            # append the temporary list to the permanent information list
            infoList.append(tempList)

    # if the query returned more than 4 cars
    if (len(carSet) >= 4):
        foundCar = False
        while (foundCar == False):
            # print a list of the info from all the queried cars
            print("Car information is in the format: make, model, year, color, plate")
            for i in range(len(carSet)):
                print(str(i+1) + ". " + str(infoList[i][0][0]) + ",", end = ' ')
                print(str(infoList[i][0][1]) + ",", end = ' ')
                print(str(infoList[i][0][2]) + ",", end = ' ')
                print(str(infoList[i][0][3]) + ",", end = ' ')

            	# if the car has a registered owner
                if (len(infoList[i]) > 1):
                    print(str(infoList[i][1][0]))
                # otherwise, it doesnt have a plate
                else:
                    print("no plate")

            # matchCar is the index+1 of the matching car in the infoList
            matchCar = input("Enter the number of the car you are looking for: ")

            validNum = False
            while (validNum == False):
                try:
                    matchCar = int(matchCar)
                    if (matchCar <= len(carSet) and matchCar > 0):
                        validNum = True
                    else:
                        print("Error. Please enter a number that is within the listed values.")
                except:
                    print("Error. Please enter a number (ie 1, 2, 3, ...) that is within the listed values.")

                if (validNum == False):
                    matchCar = input("Enter the number of the car you are looking for: ")

            # the index of the car will be at the entered value minus one
            carInd = matchCar - 1

            print("The make is " + str(infoList[carInd][0][0]), end = '. ')
            print("The model is " + str(infoList[carInd][0][1]), end = '. ')
            print("The year is " + str(infoList[carInd][0][2]), end = '. ')
            print("The color is " + str(infoList[carInd][0][3]), end = '. ')

            if (len(infoList[carInd]) > 1):
                print("The plate is " + str(infoList[carInd][1][0]), end = '. ')
                print("The latest registration date is " + str(infoList[carInd][1][1]), end = '. ')
                print("The registration expiry date is " + str(infoList[carInd][1][2]), end = '. ')
                print("The name of the person listed in the record is " + str(infoList[carInd][1][3]) + ' ' + str(infoList[carInd][1][4]), end = '.\n')
            else:
                print("This car has no owner.")

            ans = input("Was this the car you were looking for?(y for yes): ")
            if (ans.lower() == 'y'):
                foundCar = True
    else:
        currCar = 1
        for carInd in range(len(infoList)):
                if (len(infoList) > 1):
                        print("The information for car number " + str(currCar) + " is:")
                        currCar += 1
                else:
                        print("The car's information is:")

                print("The make is " + str(infoList[carInd][0][0]), end = '. ')
                print("The model is " + str(infoList[carInd][0][1]), end = '. ')
                print("The year is " + str(infoList[carInd][0][2]), end = '. ')
                print("The color is " + str(infoList[carInd][0][3]), end = '. ')

                if (len(infoList[carInd]) > 1):
                    print("The plate is " + str(infoList[carInd][1][0]), end = '. ')
                    print("The latest registration date is " + str(infoList[carInd][1][1]), end = '. ')
                    print("The registration expiry date is " + str(infoList[carInd][1][2]), end = '. ')
                    print("The name of the person listed in the record is " + str(infoList[carInd][1][3]) + ' ' + str(infoList[carInd][1][4]), end = '.\n')
                else:
                    print("This car has no owner.")

