import connection as con
import getpass
import re
import registry_agent as r_a
import traffic_officer as t_o

def log_in():
    #Returns a tuple that contains a login boolean=true if the login was valid 
    #and the info of the user, if the login didn't proceed returns false and an empty tuple    

    print('Please input your uid and your password ')

   
    while True:
        uid = input('UID :: ')                        #ask user to input the uid and password          
        password = getpass.getpass('Password :: ')

        if re.match("^[A-Za-z0-9_]*$", uid) and re.match("^[A-Za-z0-9_]*$", password):        #check no special charaters are being inputed 
            con.c.execute(""" SELECT * FROM users WHERE uid=:uid AND pwd=:password """, {'uid':uid, 'password':password})   #execute the query
            user_info=con.c.fetchone()                                                  #retrieves the result of the query
            if user_info != None:                                                   #if the result is not empty ends the while loop and returns the user_info and a boolean True
                account_type = user_info['utype']
                if account_type == 'a':
                    r_a.agent_terminal(user_info)
                else:
                    t_o.officer_terminal()

        response = input("Login Failed, Would you like to try again (y/n)?")
        if response.lower != 'y':
            return
    return
             

def main():
    print('Welcome to the mini project 1 database')

    while True:
        intent = input("Please input 'L' to login or 'Q' to quit")

        if intent.lower() == 'l':
            log_in()
        elif intent.lower() == 'q':
            break
        else:
            print("Invalid input")
    con.connection.commit()
    con.c.close()

    return

main()