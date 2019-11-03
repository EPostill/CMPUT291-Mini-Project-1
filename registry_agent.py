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

def renew_vehicle_reg():
    pass

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
