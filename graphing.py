import requests
import os
import json


import matplotlib.pyplot as plt
import pprint


# HELPER functions
def bar_chart(x , y , X_label , Y_label, Title , color_input):
    plt.style.use('ggplot')
    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, y, color= color_input ) #STR ex: "green"
    plt.xlabel(X_label)
    plt.ylabel(Y_label)
    plt.title(Title)
    plt.xticks(x_pos, x)
    # manage picture scale 
    # plt.subplots_adjust(left=None, bottom=0, right=None, top= 0.5, wspace=None, hspace=None)
    plt.xticks(rotation=90)
    plt.show()
def piechart(labels , sizes):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
def linePlot(xList, yList, title, xLabel, yLabel):
    plt.plot(xList, yList)
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.show()

def display_all_users(data):
    count = 0
    users = []
    for user_id in data:
        username = data[user_id]['username']
        print(  f'{count} : {username}'  )
        users.append(user_id)
        count+=1
    choice = int(input("\nplease choose a user: "))
    return users[choice]




# CORE FUNCTIONALITY
def user_Current_emotions_pie(data, user):
    labels = (data[user]["overallMessageEmotion_current"].keys())
    sizes = []
    for key in data[user]["overallMessageEmotion_current"].keys():
        sizes.append(data[user]["overallMessageEmotion_current"][key]*100)
    piechart(labels, sizes)

def server_Current_emotions_pie(data):
    avg_arr = []
    for username in data:
        user_data = data[username] 
        users_emotions_arr = user_data['overallMessageEmotion_arr']
        users_emotions_current = user_data['overallMessageEmotion_current']

        # # debug
        # pprint.pprint(users_emotions_arr)
        # print(users_emotions_current)
        # print('----------\n')

        avg_arr.append(users_emotions_current)

    server_emotions = {
        'anger': [],
        'disgust': [],
        'fear': [],
        'joy': [],
        'sadness': []
    }

    for dictionary in avg_arr:
        server_emotions['anger'].append(dictionary['anger'])
        server_emotions['disgust'].append(dictionary['disgust'])
        server_emotions['fear'].append(dictionary['fear'])
        server_emotions['joy'].append(dictionary['joy'])
        server_emotions['sadness'].append(dictionary['sadness'])


    sizes = []
    for x in server_emotions.keys():
        server_emotions[x] = sum(server_emotions[x]) / len(server_emotions[x])
        sizes.append(server_emotions[x])

    # debug
    pprint.pprint(server_emotions)

    # pie chart
    piechart(server_emotions.keys() , sizes)





# MAIN DEBUG
server = '782665843640238131'
data = requests.get(f"http://18.220.80.113:8080/?server={server}").json()
username = display_all_users(data)



# USER SPECIFIC
user_Current_emotions_pie(data, username)

# SERVER SPECIFIC
# server_Current_emotions_pie(data)