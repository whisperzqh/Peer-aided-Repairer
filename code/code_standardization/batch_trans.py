from trans import get
import os

old_dir = '../../Defects4DS/student_submissions'
new_dir = '../../Defects4DS/student_submissions_standardization'

problems_list = os.listdir(old_dir)
for problems in problems_list:
    new_problems = os.path.join(new_dir, problems)
    old_problems = os.path.join(old_dir, problems)
    if not os.path.exists(new_problems):
        os.mkdir(new_problems)
    users_list = os.listdir(old_problems)
    for user in users_list:
        new_user = os.path.join(new_problems, user)
        if not os.path.exists(new_user):
            os.mkdir(new_user)
        old_user = os.path.join(old_problems, user)
        if not os.path.exists(os.path.join(new_user, 'buggy.c')):
            with open(os.path.join(old_user, 'buggy.c'), 'r', encoding='utf8', errors="ignore") as f:
                print(os.path.join(old_user, 'buggy.c'))
                content = f.read()
                content = get(content)
                with open(os.path.join(new_user, 'buggy.c'), 'w', encoding='utf8', errors="ignore") as ff:
                    ff.write(content)
        if not os.path.exists(os.path.join(new_user, 'correct.c')):

            with open(os.path.join(old_user, 'correct.c'), 'r', encoding='utf8', errors="ignore") as f:
                print(os.path.join(old_user, 'correct.c'))
                content = f.read()
                content = get(content)
                with open(os.path.join(new_user, 'correct.c'), 'w', encoding='utf8', errors="ignore") as ff:
                    ff.write(content)

