user_ids = {
    'abang' : [],
    'hr'    : []
    }

def is_abang(user_id):
    if(user_id in user_ids["abang"]):
        return True
    else:
        return False

def is_hr(user_id):
    if(user_id in user_ids["hr"]):
        return True
    else:
        return False

def add_abang_id(user_id):
    user_ids["abang"].append(user_id)

def add_hr_id(user_id):
    user_ids["hr"].append(user_id)

def del_abang_id(user_id):
    user_ids["abang"].remove(user_id)

def del_hr_id(user_id):
    user_ids["hr"].remove(user_id)

#Dummy commit
