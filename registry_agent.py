import connection as con
from datetime import date

def agent_terminal():
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
            register_birth()
        elif intent == 2:
            register_marriage()
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




def register_birth():
    pass


def register_marriage():
    pass

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
    c.execute("select expiry from registrations where regno = :num;", {"num":userRegno})
    res = c.fetchall()
    try:
        # this throws an error if the query is not as expected, ie empty or an int/str
        res[0][0]
        # if above didnt throw an error, query is valid
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
        validQuery, userRegno, res = query(userRegno,cur)

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
    c.execute("update registrations set expiry = :date where regno = :num;", {"date":newExpiry, "num":userRegno})

    c.close()

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

def process_payment():
    pass

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
