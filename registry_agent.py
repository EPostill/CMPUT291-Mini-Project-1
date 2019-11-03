import connection as con

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
    pass

def process_payment():
    pass

def get_driver_abstract():
    pass