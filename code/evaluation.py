import threading
import time
import xml.etree.ElementTree as et
import re
import os
import json
import subprocess

dataset_dir = "../Defects4DS"


def extract_code(message_: str, model):
    if model == 'chatgpt':
        start = message_.find('#include')
        stop = 0
        for stop in range(start, len(message_)):
            if message_[stop] == '`':
                stop -= 1
                break
        return message_[start: stop + 1]
    elif model == 'codellama':
        start = message_.find('[Correct Code]')
        stop = message_.find('[End of Correct Code]')
        if stop < 0:
            code = message_[start + len('[Correct Code]'):].strip()
        else:
            code = message_[start + len('[Correct Code]'): stop].strip()
        return code
    else:
        print("model name error")


def obtain_testcase():
    tree = et.parse(dataset_dir + '/test_cases/' + pid + '.xml')
    root = tree.getroot()
    tc_inputs, tc_outputs = [], []
    for elem in root.iter('testDataSet'):
        for case in elem:
            ipt = case.find('input').text.strip()
            opt = case.find('output').text.strip()
            ipt = re.sub(r'\s+', " ", ipt)
            opt = transform_output(opt)
            tc_inputs.append(ipt)
            tc_outputs.append(opt)
    return tc_inputs, tc_outputs


def transform_output(output: str):
    lst = output.split("\n")
    opt = ""
    for s in lst:
        opt += (s.strip() + "\n")
    return opt


def judge_code(filename):
    os.system("gcc -std=c99 " + user_dir + "/" + filename + ".c -o " + user_dir + "/temp.exe")
    code_result = []
    for i in range(len(test_case_inputs)):
        try:
            opt = run_code(test_case_inputs[i], user_dir + "/temp.exe").strip()
        except Exception as e:
            print(e)
            opt = ""
        opt = transform_output(opt)
        if opt == test_case_outputs[i]:
            code_result.append(True)
        else:
            code_result.append(False)
    if os.path.exists(user_dir + "/temp.exe"):
        os.remove(user_dir + "/temp.exe")
    return code_result


def run_code(ipt, exe):
    threshold = 10000
    cmd_output = ''
    character_count = 0

    with open('tem.txt', 'w', encoding='utf-8') as f1:
        f1.write(ipt)
    f1.close()
    f2 = open('tem.txt', 'r', encoding='utf-8')
    process = subprocess.Popen([exe], stdin=f2, stdout=subprocess.PIPE)

    def terminate(process_):
        print("timeout.")
        process_.terminate()

    timer = threading.Timer(5, terminate, args=[process])
    timer.start()

    while True:
        output = process.stdout.readline()
        if not output:
            break
        cmd_output += output.decode(encoding='gbk')
        character_count += len(output.decode(encoding='gbk'))
        if character_count > threshold:
            process.kill()
            break
    timer.cancel()
    return cmd_output


def calculate_successful_trials():
    statistics[pid]['total'] += 1
    correct_trial = 0
    for file in filenames:
        code_result = user_result['judge_results'][file]
        if False not in code_result:
            correct_trial += 1
    if correct_trial >= 3:
        statistics[pid]['successful'] += 1
    user_result["successful trials"] = correct_trial
    user_result["successful repair"] = (correct_trial >= 3)
    return correct_trial


def write_output_code_to_file(file_, idx, model):
    with open(user_dir + "/" + file_ + ".c", 'w+') as f_:
        f_.write(extract_code(llm_outputs[idx]["output"], model))


def get_index_in_outputs_jsonl():
    index = []
    for j in range(len(llm_outputs)):
        if llm_outputs[j]['problem_id'] == pid and llm_outputs[j]['user_id'] == uid:
            index.append(j)
        if len(index) == 5:
            break
    return index


if __name__ == '__main__':
    model = "chatgpt"  # model = "codellama"
    pids = ["problemID_1", "problemID_2", "problemID_3", "problemID_4"]
    filenames = ["repair0", "repair1", "repair2", "repair3", "repair4"]
    results = []  # the results of all submissions

    # load the outputs of LLM
    llm_outputs = []
    with open(dataset_dir + "/outputs_" + model + ".jsonl") as f:
        for l in f.readlines():
            llm_outputs.append(json.loads(l))

    # initialize the statistics
    statistics = {"problemID_1": {"successful": 0, "total": 0}, "problemID_2": {"successful": 0, "total": 0},
                  "problemID_3": {"successful": 0, "total": 0}, "problemID_4": {"successful": 0, "total": 0}}

    for pid in pids:
        problem_dir = dataset_dir + "/student_submissions/" + pid
        # get test cases
        test_case_inputs, test_case_outputs = obtain_testcase()

        for uid in os.listdir(problem_dir):
            user_dir = problem_dir + "/" + uid
            user_result = {'problem_id': pid, 'user_id': uid, 'judge_results': {}}

            # get the index of outputs of current uid
            index = get_index_in_outputs_jsonl()

            # judge
            if len(index) == 5:
                for i in range(5):
                    write_output_code_to_file(filenames[i], index[i], model)
                    user_result['judge_results'][filenames[i]] = judge_code(filenames[i])
                    os.remove(user_dir + "/" + filenames[i] + ".c")
                calculate_successful_trials()
                print(model + ": " + pid + " " + uid + ": number of successful trials is " + str(user_result['successful trials']))
                results.append(user_result)
            else:
                print(model + ": " + pid + " " + uid + ": not ready")
                continue

    print(statistics)
    # write results to file
    f = open(dataset_dir + "/results_" + model + ".jsonl", 'w', encoding='utf-8')
    for i in results:
        json.dump(i, f, ensure_ascii=False)
        f.write('\n')
    os.remove('tem.txt')
