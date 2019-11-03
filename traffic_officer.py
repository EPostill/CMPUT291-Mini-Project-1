import connection as con

def officer_terminal():
    print("Welcome, as a traffic officer you are able to perform the following actions")
    print("1 - Issue a ticket")
    print("2 - Find a car owner")
    print("3 - Log out")

    while True:
        intent = input("please type the number of the action you would like to perform")
        if intent == 1:
            issue_ticket()
        elif intent == 2:
            find_car_owner()
        elif intent == 3:
            return
        else:
            print("Invalid input")


def issue_ticket():
    pass

def find_car_owner():
    pass