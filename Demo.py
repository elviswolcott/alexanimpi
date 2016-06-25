state = [7, 5, 3];
waitingA = False
turn = 1;
while(True):
    if(turn == 1): #computer turn
        xored = state[0] ^ state[1] ^ state[2]
        if xored == 0:
            if(state[0] != 0):
                target = 0;
                number = 1;
            elif(state[1] != 0):
                target = 1;
                number = 1;
        else:
            for z in range(3):
                s = state[z] ^ xored
                if s <= state[z]:
                    target = z;
                    number = state[z] - s;
                    if(number == 0):
                        number == 1;
        turn = 2;
    elif(turn == 2): #player turn
        waiting = True;
        while(waiting):
            if(not waitingA):
                target = int(input("Choose a row")) - 1;
                if(target > -1 and target < 3):
                    print("Acknowledged");
                    skip = False;
                else:
                    print("Invalid input");
                    skip = True;
            if(not skip):
                number = int(input("Choose how many to take"));
                if(number > 0 and number < state[target] + 1):
                    waiting = False;
                    waitingA = False;
                else:
                    print("Invalid input");
                    waitingA = True;
        turn = 1;
    state[target] = state[target] - number;
    print("Row 1: " + str(state[0]) + " Row 2: " + str(state[1]) + " Row 3: " + str(state[2]));
    if(state[0] == 0 and state[1] == 0 and state[2] == 0):
        print("Game over!");
        if(turn == 1):
            print("You win.");
        else:
            print("You lost.");
        print("Quit the program");
        while(True):
            a = 1;
            #loop out
