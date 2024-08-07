import os
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
            model="llama3-70b-8192", )

import time
from groq import Groq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# 2nd case missing multiple input
import json
import ast
import re

# Regex pattern to match dictionaries
pattern = re.compile(r"\{[^{}]+\}")

# initial_prompt = PromptTemplate(
#     template="""system
# You are an assistant capable of helping employees apply for leave based on the leave information they provide. Analyze the information and store it 
# in the correct dictionary key-value pairs. If the user provides the dates in reverse order, do not fill the from_date and to_date values. Dates should be in incremental
# order, like between 1 to 31, not 31 to 1. If related values are not in the information, then don't fill that key. select_leave_types should be from this 
# list: [Bereavement Leave, Leave Without Pay, Marriage Leave, Paternity Leave, Privilege Leave, Sick Leave] do not fill the value of select_leave_types if user not clearly discribe about type of leave. Correct any spelling errors in the leave type and store
# it if it's from the list. In your answer, provide only the dictionary, nothing more. The dictionary is: {json} 
# user
# Here is my leave information: {description}
# assistant
# """,
#     input_variables=["json", "description"]
# )

initial_prompt = PromptTemplate(
    template="""system
You are an assistant capable of helping employees apply for leave based on the leave information they provide. Analyze the information and store it 
in the correct dictionary key-value pairs. If the user provides the dates in reverse order, do not fill the from_date and to_date values. Dates should be in incremental
order, like between 1 to 31, not 31 to 1. If related values are not in the information, then don't fill that key. Select_leave_types should be from this 
list: [Bereavement Leave, Leave Without Pay, Marriage Leave, Paternity Leave, Privilege Leave, Sick Leave]. Do not fill the value of select_leave_types if the user does not clearly describe the type of leave. 
Correct any spelling errors in the leave type and store it if it's from the list. 
In your answer, provide only the dictionary, nothing more. The dictionary is: {json} 
user
Here is my leave information: {description}
assistant
""",
    input_variables=["json", "description"]
)


# Define the prompt template for asking missing information
missing_info_prompt = PromptTemplate(
    template="""system
You are an assistant helping to fill out a leave request form. The following information is missing: {missing_fields}. Please ask the user to provide this information.
Assistant, below is the type of required field. If the user did not fill that criteria, give options as below for the relevant missing value:
select_leave_types: [Bereavement Leave, Leave Without Pay, Marriage Leave, Paternity Leave, Privilege Leave, Sick Leave].
If the user provided dates in reverse order, do not fill in the date values. Ask the user to give the dates in the correct order, and explain why the user's dates are not eligible.
""",
    input_variables=["missing_fields"]
)

fill_rest_prompt = PromptTemplate(
    template="""system
You are an assistant to fill relevant information in dictionary empty values from the user's answers. Check this dictionary for empty value keys: {missing_fields}. 
For the reason_for_leave field, fill in the value only if the user provides a proper reason for leave. Do not add anything more in the reason field from your side.
If the type of leave is not included from this list [Bereavement Leave, Leave Without Pay, Marriage Leave, Paternity Leave, Privilege Leave, Sick Leave],
do not fill the value of select_leave_types if user not clearly say about type of leave.
If the user provides the dates in reverse order, do not fill the from_date and to_date values. Dates should be in incremental order, like between 1 to 31, not 31 to 1.
Analyze the information and store it in the correct dictionary key-value pairs, and in your answer provide only the dictionary, nothing more.
This is the user's message: {user_answer}
assistant""",
    input_variables=["missing_fields","user_answer"]
)
# Define the leave_request dictionary
with open('C:/projcects/leave_chatbot/notebook/leave_request.json', 'r') as json_file:
    leave_request = json.load(json_file)

# Convert the leave_request dictionary to a JSON string
leave_request_json =  leave_request #json.dumps(leave_request)

#user_input = 'I want to leave from 15th August to 19th August'# for LWP leave.'
user_input = str(input('reason >>>>'))

# Define the visual generator for initial response
visual_generator_initial = initial_prompt | llm | StrOutputParser()

fill_all_value = fill_rest_prompt | llm | StrOutputParser()

# Invoke the visual generator with the JSON string and user description
initial_response = visual_generator_initial.invoke({"json": leave_request_json, "description": user_input})

# Print the initial response
print("Initial response:", initial_response)
initial_response = pattern.findall(initial_response)
print("1 lo:", initial_response[0])
initial_response = ast.literal_eval(initial_response[0])
# log_chat(user_input, initial_response)
######################
with open('leave_request_ans.json', 'w') as json_file:
    json.dump(initial_response, json_file, indent=4)

with open('C:/projcects/leave_chatbot/notebook/leave_request_ans.json', 'r') as json_file:
    leave_request = json.load(json_file)

# Check for missing fields  
missing_fields = [key for key, value in leave_request.items() if not value]

if missing_fields:
    # If there are missing fields, prompt the user for them
    while missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        
        # Define the visual generator for missing information
        visual_generator_missing_info = missing_info_prompt | llm | StrOutputParser()
        
        # Get the response for missing fields
        missing_info_response = visual_generator_missing_info.invoke({"missing_fields": missing_fields_str})
        
        print("Missing information response:", missing_info_response,'therrrrrr end')

        with open('C:/projcects/leave_chatbot/notebook/leave_request_ans.json', 'r') as json_file:
            leave_request = json.load(json_file)

        user_input_02 = str(input('>>>>>>>'))
        # print(f"Hello, {user_input_02}!")
        all_value_user = fill_all_value.invoke({"missing_fields":leave_request,"user_answer":user_input_02}) 
        all_value_user = pattern.findall(all_value_user)
        print('3ri jo promt',all_value_user,' 3jo finiiiii')

        output_file_path = 'leave_request_ans.json' #'leave.json'
        all_value = ast.literal_eval(all_value_user[0])
        with open(output_file_path, 'w') as json_file:
            json.dump(all_value, json_file)

        #     # log_chat(user_input_02, all_value)
        with open('C:/projcects/leave_chatbot/notebook/leave_request_ans.json', 'r') as json_file:
            leave_request = json.load(json_file)

        # with open('C:/projcects/leave_chatbot/notebook/leave_request_ans.json', 'r') as json_file:
        #     leave_request = json.load(json_file)
        print(leave_request,'erooooor',type(leave_request))
        missing_fields = [key for key, value in leave_request.items() if not value]


    # Save the final filled leave request dictionary to a JSON file
    output_file_path = 'leave.json'
    all_value = ast.literal_eval(all_value_user[0])
    with open(output_file_path, 'w') as json_file:
        json.dump(all_value, json_file)

    print(f"Filled leave request saved to {output_file_path}, \n\nthis is final your leave <<< {all_value} >>>")

else:
    output_file_path = 'leave.json'
    print(initial_response,'rr',type(initial_response))
    #all_value = ast.literal_eval(initial_response[0])
    with open(output_file_path, 'w') as json_file:
        json.dump(initial_response, json_file)

    print(f"Filled leave request saved to {output_file_path},\n\nthis is final your leave <<< {initial_response} >>>")
