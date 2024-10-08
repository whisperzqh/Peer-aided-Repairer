import json
import time
import openai
import os
from text_generation import Client

# add ChatGPT secret key
chat_gpt_key = " "
openai.api_key = chat_gpt_key

# add huggingface secret key
huggingface_key = " "
HF_TOKEN = os.environ.get("HF_TOKEN", huggingface_key)
API_URL = "https://api-inference.huggingface.co/models/codellama/CodeLlama-34b-Instruct-hf"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
client = Client(API_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"})

dataset_dir = "../Defects4DS"


def generate_prompt():
    # task description
    task_description = '''There is a C programming problem. Below is the problem description, the input format, \
the output format, some examples, some information about bug location, a copy of the correct code for reference, \
and a copy of the buggy code containing semantic errors that written by a student to solve the C programming \
problem. Please fix the buggy code and return the correct code. \n'''

    # problem description + input/output format + example input/output
    assignment_description = dataset_dir + '/assignment_description/' + pid + '.txt'
    desc_io_exp = open(assignment_description, 'r', encoding='utf-8').read()

    # reference code
    peer_solution_id = labeled_data[pid][uid]['peer_solution']
    peer_solution = "[Reference Code]\n" + open(problem_dir + '/' + peer_solution_id + '/correct.c', 'r', encoding='utf-8').read() + "\n[End of Reference Code]\n"

    # buggy code
    buggy_code = "[Buggy Code]\n" + open(user_dir + '/' + "buggy.c", 'r', encoding='utf-8').read() + '\n[End of Buggy Code]\n'

    # final_task_description
    final_task_description = "Please fix the code and return the correct code.\n"

    # prompt
    generated_prompt = task_description + desc_io_exp + peer_solution + buggy_code + final_task_description
    return generated_prompt


def call_gpt(prompt):
    response = None
    while True:
        success = True
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo-0613',
                messages=prompt,
                temperature=0.8
            )
        except:
            print("fail to call gpt, trying again...")
            time.sleep(2)
            success = False
        if success:
            break
    return response['choices'][0]['message']['content']


def call_codellama(prompt):
    generate_kwargs = dict(
        temperature=0.8,
        max_new_tokens=1024,
        top_p=0.95,
        repetition_penalty=1.0,
        do_sample=True,
        seed=42,
    )

    prompt += '\n[Correct Code]\n'
    stream = client.generate_stream(prompt, **generate_kwargs)
    output = prompt

    previous_token = ""
    for response in stream:
        if any([end_token in response.token.text for end_token in ["</s>", "<EOT>"]]):
            return output
        else:
            output += response.token.text
        previous_token = response.token.text
        yield output
    return output


if __name__ == '__main__':
    # get labeled data
    labeled_data = {}
    with open(dataset_dir + "/labeled_information.jsonl") as f:
        for line in f:
            item = json.loads(line)
            if item["problem_id"] in labeled_data:
                labeled_data[item["problem_id"]][item["user_id"]] = item
            else:
                labeled_data[item["problem_id"]] = {}
                labeled_data[item["problem_id"]][item["user_id"]] = item

    # get output of LLM
    pids = ["problemID_1", "problemID_2", "problemID_3", "problemID_4"]
    outputs_chatgpt, outputs_codellama = [], []
    max_trial = 5
    for pid in pids:
        problem_dir = dataset_dir + "/student_submissions/" + pid
        for uid in os.listdir(problem_dir):
            user_dir = problem_dir + "/" + uid
            prompt = generate_prompt()
            trial = 0
            while trial < max_trial:
                chatgpt_message = call_gpt([{'role': 'user', 'content': prompt}])
                outputs_chatgpt.append({"problem_id": pid, "user_id": uid, "output": chatgpt_message})
                print(pid + " " + uid + ": get code number " + str(trial) + " for ChatGPT")

                codellama_message = call_codellama(prompt)
                for value in codellama_message:
                    pass
                outputs_codellama.append({"problem_id": pid, "user_id": uid, "output": value})
                print(pid + " " + uid + ": get code number " + str(trial) + " for Code Llama")

                trial += 1

    # write the outputs to a file
    f1 = open(dataset_dir + "/outputs_chatgpt.jsonl", 'w', encoding='utf-8')
    for i in outputs_chatgpt:
        json.dump(i, f1, ensure_ascii=False)
        f1.write('\n')
    f2 = open(dataset_dir + "/outputs_codellama.jsonl", 'w', encoding='utf-8')
    for i in outputs_codellama:
        json.dump(i, f2, ensure_ascii=False)
        f2.write('\n')
