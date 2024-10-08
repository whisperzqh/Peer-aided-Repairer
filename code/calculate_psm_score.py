import json


def calculate_test_cases_pass_match_score(pid, user_1, user_2):
    test_1 = labeled_data[pid][user_1]['test_case_result']
    test_2 = labeled_data[pid][user_2]['test_case_result']
    pass_1, pass_2, same = 0, 0, 0
    for k in range(5):
        if test_1[k] and test_2[k]:
            same += 1
        if test_1[k]:
            pass_1 += 1
        if test_2[k]:
            pass_2 += 1
    if pass_2 + pass_1 == 0:
        test_cases_score = 0
    else:
        test_cases_score = (same * 2) / (pass_2 + pass_1)
    return test_cases_score


def calculate_bm25_normalization_score(score_list, bm25_score):
    sorted_score_list = sorted(score_list)
    min = sorted_score_list[0]
    max = sorted_score_list[len(sorted_score_list)-1]
    return (bm25_score - min) / (max - min)


if __name__ == '__main__':
    # get labeled data
    labeled_data = {}
    with open("../Defects4DS/labeled_information.jsonl") as f:
        for line in f:
            item = json.loads(line)
            if item["problem_id"] in labeled_data:
                labeled_data[item["problem_id"]][item["user_id"]] = item
            else:
                labeled_data[item["problem_id"]] = {}
                labeled_data[item["problem_id"]][item["user_id"]] = item

    # calculate psm score (for example)
    pid, target_user, candidate_user = "problemID_1", "userID_20088", "userID_20096"
    test_cases_pass_match_score = calculate_test_cases_pass_match_score(pid, target_user, candidate_user)
    # the calculation of data_flow_match_score and ast_match_score refers to https://github.com/reddy-lab-code-research/XLCoST/tree/main/code/translation/evaluator/CodeBLEU
    data_flow_match_score = 0.4722222222222222
    ast_match_score = 0.5784313725490197
    # the calculation of BM25 score refers to https://github.com/dorianbrown/rank_bm25
    bm25_score = 42.34534020084998
    score_list = []  # need to comlpete, contains the bm25 scores of the target_user and all other candidate users under the same problem
    bm25_normalization_score = calculate_bm25_normalization_score(score_list, bm25_score)

    psm_score = 0.25 * (test_cases_pass_match_score + data_flow_match_score + ast_match_score + bm25_normalization_score)