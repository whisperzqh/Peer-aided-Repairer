# Peer-aided Repairer: Empowering Large Models to Repair Advanced Student Assignments

- [Peer-aided Repairer: Empowering Large Models to Repair Advanced Student Assignments](#peer-aided-repairer-empowering-large-models-to-repair-advanced-student-assignments)
	- [Defects4DS](#defects4ds)
			- [1. assignment description](#1-assignment-description)
			- [2. student submissions](#2-student-submissions)
			- [3. test cases](#3-test-cases)
			- [4. codebook.pdf](#4-codebookpdf)
			- [5. labeled\_information.jsonl](#5-labeled_informationjsonl)
			- [6. comparison with ITSP](#6-comparison-with-itsp)
	- [Code](#code)
			- [1. run.py](#1-runpy)
			- [2. evaluation.py](#2-evaluationpy)
			- [3. calculate\_psm\_score.py](#3-calculate_psm_scorepy)
			- [4. code\_standardization](#4-code_standardization)
			- [pipeline](#pipeline)
	- [questionaire\_results.xlsx](#questionaire_resultsxlsx)


## Defects4DS

#### 1. assignment description

Inside this folder are the descriptions of the four assignments, including problem description, input/output form, and example input/output.

#### 2. student submissions

Inside this folder are the students' submissions. 
Each submission includes two code variations: a correct code that successfully passes all five test cases, and a buggy code that represents the student’s last incorrect attempt.
The buggy codes contain semantic errors only, and the discrepancy between the correct code and the buggy code is limited to a maximum of five lines. 

#### 3. test cases

Inside this folder are the test cases for the four assignments, used to evaluate the correctness of the submitted code.

#### 4. codebook.pdf

Our dataset divides bugs into 7 main categories and 30 subcategories. 
This file contains detailed information of the classification, and we provide an example for each bug type.

#### 5. labeled_information.jsonl

This file contains the labeled information, test case results of the buggy code, and the peer solution selected by PSM score for each submission.

```json
{
	"problem_id": "problemID_3",
	"user_id": "userID_21161",
	"bug_list": [
		{
			"bug_line": "76",
			"bug_type": "V_3",
			"repair_type": "4",
			"related_to_other_bugs": 0
		}
	],
	"test_case_result": [false, false, true, true, true],
	"peer_solution": "userID_20353"
}
```

The following is the description of each item:

- **problem_id**: problem ID.
- **user_id**: user (student) ID.
- **bug_list**: the bug information from 4 dimensions.
  - **bug_line**: the line number(s) where the bug is present.
  - **bug_type**: the type of bug encountered. Only identifiers are marked here, and the corresponding complete descriptions of bug types can be found in the codebook.
  - **repair_type**: the potential methods to fix the bug. The numbers 1-4 correspond to *statement addition*, *statement deletion*, *position modification* and *statement modification*.
  - **related_to_other_bugs**: whether the bug is related to other bugs in the same file. The number 1 means *True* and 0 means *False*.
- **test_case_result**: the results of the buggy code passing the test cases.
- **peer_solution**: the user ID of the peer solution selected by PSM score (all the coefficients are set to 0.25).

#### 6. comparison with ITSP

We conducted an in-depth comparison between Defects4DS dataset and ITSP dataset to explain the motivation for creating Defects4DS. The detailed information is inside this folder.

## Code

#### 1. run.py

This file provides code for generating prompts and calling LLM to obtain its output.

#### 2. evaluation.py

This file provides an evaluation method for C language code and a calculation method to judge whether the code is fixed. 

#### 3. calculate_psm_score.py

This file provides the calculation methods of PSM score.
The calculation of *bm25_score* refers to https://github.com/dorianbrown/rank_bm25.
The calculation of *data_flow_match_score* and *ast_match_score* refers to https://github.com/reddy-lab-code-research/XLCoST/tree/main/code/translation/evaluator/CodeBLEU.

#### 4. code_standardization

This folder contains code for standardizing C language code to alleviate the impact of different identifier naming.

#### pipeline

```
# To standardize the C language code
bash code_standardization/build/build.sh
python code_standardization/batch_trans.py

# To calculate the PSM score
python calculate_psm_score.py

# To generate the prompt and obtain the output of LLM
# First edit the run.py file, change the variables 'chat_gpt_key' and 'huggingface_key' to your own secret keys
python run.py

# To evaluate the generated code
# First edit the evaluation.py file, change the variable 'model' to the name of the model whose results need to be calculated
python evaluation.py
```

## questionaire_results.xlsx

This file provides original data of the user study in Section 7.3.3 of our paper.
