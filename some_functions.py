import requests
from bs4 import BeautifulSoup
import config as cf

def logging():
    url = 'https://rosstudsport.ru/user/login'
    user_agent_val = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

    # define headers
    my_headers = {
        "User-Agent": user_agent_val,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,image/avif,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # start a session
    session = requests.Session()
    session.headers.update(my_headers)
    r = session.get(url)

    # find _csrf in html code
    soup = BeautifulSoup(r.text, "html.parser")
    _csrf = soup.find("input", {"name": "_csrf"}).get("value")

    #  Certain websites check the Referer header for security reasons,
    #  expecting that requests originate from expected pages. It's a way
    #  of verifying that the request comes from a legitimate source. In
    #  this case, we set the Referer header to the URL of the login page,
    #  indicating that our request comes from there. It's not always required,
    #  but some websites use this to protect against CSRF (Cross-Site
    #  Request Forgery) attacks or to provide additional security.
    session.headers.update({'Referer': url})

    # When updating the headers with the Referer using session.headers.update({'Referer': url}),
    # it can overwrite the original User-Agent value. So, specifying the User-Agent
    # again ensures that we maintain the user agent value in the headers.
    # It works without specifying User-Agent again, but just in case.
    session.headers.update({'User-Agent': user_agent_val})

    post_request = session.post(url, {
        '_csrf': _csrf,
        'login-form[login]': cf.EMAIL,
        'login-form[password]': cf.PASSWORD,
        'login-form[rememberMe]': '0',
        'ajax': 'login-form-modal'
    })

    post_soup = BeautifulSoup(post_request.text, 'html.parser')

    # Check for specific elements indicating succeded login.
    login_succeded = ('АДМИНИСТРАТОРОВ' in post_soup.get_text().split()) # CHANGE

    print(post_request.status_code) # 200

    if not login_succeded:
        print("Login failed!")
    else:
        print("Login succeeded!")
        # print(post_request.text)
    return session

def check_person(text, person):
    if person[0] in text: # check existance
        return False
    if any(ch.isdigit() for ch in person[0]): # check digits in name
        return False
    if '@' in person[4]: # check email
        return True
    return False
def add_person(session, person):

    first_new_sportsman_url = "https://rosstudsport.ru/cp/user/search/create?role=player"
    profile_url = "https://rosstudsport.ru/cp/user/search/update-profile?id=*" # replace * with inner id later

    url = 'https://rosstudsport.ru/user/login'
    user_agent_val = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})

    '''                                                 First page                                                  '''
    get_page_1 = session.get(first_new_sportsman_url)
    soup = BeautifulSoup(get_page_1.text, "html.parser")
    _csrf = soup.find("input", {"name": "_csrf"}).get("value")
    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})

    post_page_1 = session.post(first_new_sportsman_url, {
        "_csrf": _csrf,
        "User[email]": person[4],
        "User[phone]" : person[1],
        "User[username]": person[0],
        "User[password]": '12345',
        "User[club_id]": "28"
    })

    if "Этот email уже используется" in post_page_1.text: # if person exists, stop
        print("Already created", person[4])
        return 0 # for added_sportsmen_counter

    # get inner user id to replace * in second_new_sportsman_url
    soup2 = BeautifulSoup(post_page_1.text, "html.parser")
    inner_id = str(soup2.findAll(class_='active')[2]).split("id=")[1].split('">')[0]
    profile_url = profile_url.replace("*", inner_id)

    '''                                                 2nd page: Profile                                                 '''

    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})

    full_name_list = person[0].split()

    post_page_2 = session.post(profile_url, {
        "_csrf": _csrf,
        "Profile[first_name]": full_name_list[1],
        "Profile[last_name]": full_name_list[2],
        "Profile[middle_name]": full_name_list[0],
        "Profile[birthday]": person[2],
        "Profile[position]": ""
    })
    # print(post_page_2.text)

    '''                                                 3rd page: Roles                                                 '''

    roles_url = "https://rosstudsport.ru/cp/user/search/update-roles?id=*".replace("*", inner_id)
    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})

    full_name_list = person[0].split()

    post_page_3 = session.post(roles_url, {
        "_csrf": _csrf,
	    "roles[128]": "0",
	    "roles[8192]": "0",
	    "roles[131072]": "0",
	    "player-form[last_name]": full_name_list[2],
	    "player-form[first_name]": full_name_list[1],
	    "player-form[middle_name]": full_name_list[0],
	    "player-form[email]": person[4],
        "player-form[institution_id]": "28", # sets BMSTU
        "player-form[club_id]": "28", # Sets Bauman Pandas
        "roles[32768]": "0",
        "Staff[last_name]": full_name_list[2],
        "Staff[first_name]": full_name_list[1],
        "Staff[middle_name]": full_name_list[0]
    })

    soup3 = BeautifulSoup(post_page_3.text, "html.parser")
    profile_inner_id = str(soup3.findAll(class_='alert alert-mint')).split('profile/')[1].split('/update')[0]
    # print(profile_inner_id)
    # print(post_page_3.text)

    '''                                                 4th page: Profile information                                              '''
    profile_information_link = "https://rosstudsport.ru/cp/player/profile/*/update".replace('*', profile_inner_id)

    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})
    post_page_4 = session.post(profile_information_link, {
	    "_csrf": _csrf,
	    # "player-form[photo_b64]": person[8], # !!! need to upload photo manually from the computer
	    "player-form[gender]": str('woman' if person[7] == 'ж' else 'man'),
	    "player-form[birthday]": person[2],
	    "player-form[birthplace]": "Москва",
	    "player-form[faculty]": str(person[5][:2]),
	    "player-form[admission_year]": '20' + str(person[6][:2]),
	    "player-form[graduation_year]": int('20' + str(person[6][:2])) + 6 - 4 * ('М' in person[6]) - 2 * ('Б' in person[6]),
        "player-form[phone]": person[1]
    })
    # print(post_page_4.text)

    '''                                                 5th page: Social networks                                              '''
    # Notice: you can't add telegram. Only VK.
    social_link = "https://rosstudsport.ru/cp/player/profile/*/socials".replace("*", profile_inner_id)
    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})
    post_page_5 = session.post(social_link, {
	    "_csrf": _csrf,
	    "Social[0][social]": ("tg" if person[10] == "Телеграм" else "vk"),
	    "Social[0][url]": person[9],
        "Social[0][rank]": "0"
    })
    # print(post_page_5.text)
    print(f'added: {person[0]}. e-mail: {person[4]}')
    return 1 # for added_sportsmen_counter



def check_and_add(session, people):
    sportsmen_url = "https://rosstudsport.ru/cp/user/search/players"

    url = 'https://rosstudsport.ru/user/login'
    user_agent_val = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})

    trying = session.get(sportsmen_url)
    # print(people)
    added_sportsmen_counter = 0
    for person in people[1:len(people)]:
        if check_person(trying.text, person):
            added_sportsmen_counter += add_person(session, person)
    print(f'''Totally added : {added_sportsmen_counter}''')