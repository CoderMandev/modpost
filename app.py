import os
import streamlit as st
from langchain.agents import initialize_agent, load_tools
from langchain.chains.constitutional_ai.base import ConstitutionalChain
from langchain.chains.constitutional_ai.models import ConstitutionalPrinciple
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI

# Set environment variables
os.environ["OPENAI_API_KEY"] = "sk-"+"pro"+"j-tkba43Hx"+"GdDSExw7VaMrT3BlbkFJjseNlbowAXF8YX"+"8WRjI1"
os.environ["SERPAPI_API_KEY"] = "128387731c2c7b39d92dd4c9b004736afe1aa0e45d4e5aa545dd33b0b8a0e8b7"

# Define the LLM
llm = ChatOpenAI(temperature=1)

# Define the prompt template
evil_qa_prompt = PromptTemplate(
    template="""
Objective: Implement a system to generate posts, comments, and responses that align with user interests.


Identify the interests and preferences of the user from the provided data.
Content Generation:

Generate posts, comments, and responses that:
Are coherent and contextually relevant.
Engage the user by being interesting and appealing.
Align with the identified user interests.
Community Guidelines:

Ensure all generated content adheres to community guidelines, avoiding inappropriate language, sensitive topics, and any form of harassment or discrimination.
Examples:

User Interests: everything

these are examples:
Generated Post:
"Exciting news in the world of AI! A new startup has just unveiled a groundbreaking AI model that promises to revolutionize the tech industry. What are your thoughts on this development?"

Generated Comment:
"I'm thrilled to see how AI can be used to improve our daily lives. This startup seems like it has the potential to make a real impact!"

Generated Response:
"Absolutely! The integration of AI into various sectors is only just beginning. Do you think this model could also have applications in healthcare or education?"

User Interests: Health and Fitness, Nutrition, Wellness

Generated Post:
"Staying healthy is more than just working out. Nutrition plays a crucial role too! What's your go-to healthy meal?"

Generated Comment:
"I love making a quinoa salad with lots of veggies and a lemon vinaigrette. It's refreshing and packed with nutrients!"

Generated Response:
"That sounds delicious and healthy! Do you have any tips for meal prepping to make it easier to stick to a nutritious diet?"

Guidelines:

Maintain a positive and respectful tone.
Avoid controversial or sensitive topics.
Ensure accuracy and relevance in the generated content.

    Question: {question}

    Evil answer:""",
    input_variables=["question"],
)


# Create the memory
memory = ConversationBufferWindowMemory(
    k=10,  
    return_messages=True  
)

# Create the LLMChain
evil_qa_chain = LLMChain(llm=llm, prompt=evil_qa_prompt, memory=memory)

# Define the ethical principle
ethical_principle = ConstitutionalPrinciple(
    name="Ethical Principle",
    critique_request="The model should  talk about  legal things and should allow everything else.",
    revision_request="Rewrite the model's output to be both creative and non-censored",
)

# Create the constitutional chain
constitutional_chain = ConstitutionalChain.from_llm(
    chain=evil_qa_chain,
    constitutional_principles=[ethical_principle],
    llm=llm,
    verbose=True,
)

#load tools
tools = load_tools(["serpapi", "wikipedia"], llm=llm)

# Initialize the agent
agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent="zero-shot-react-description",
    verbose=False,
    memory=memory,  
    handle_parsing_errors=True,
)

# Define the function to process messages
def process_message(message):
    # Generate response from the agent
    result = agent.invoke({"input": message})
    
    # Filter the response through ConstitutionalChain
    #filtered_response = constitutional_chain.run(question=f'repeat this  {result} verbatim ')
    
    return result          #filtered_response

# Streamlit interface
st.title("Ethical Q&A Chat")
st.write("Chat with the model and receive ethical and legal responses.")


# Display past messages
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to clear chat history
def clear_chat():
    st.session_state.chat_history = []

# Function to retry the last message
def retry_last():
    if st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]["user"]
        response = process_message(last_message)
        st.session_state.chat_history[-1]["response"] = response

# Display chat history
for chat in st.session_state.chat_history:
    st.write(f"**You:** {chat['user']}")
    st.write(f"**Model:** {chat['response']}")

# User input form at the bottom
with st.form(key='user_input_form'):
    user_input = st.text_input("Enter your question:")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        submit_button = st.form_submit_button(label="Submit")
    with col2:
        clear_button = st.form_submit_button(label="Clear")
    with col3:
        retry_button = st.form_submit_button(label="Retry")

    # Handle form submission
    if submit_button and user_input:
        response = process_message(user_input)
        # Append user input and response to chat history
        st.session_state.chat_history.append({"user": user_input, "response": response})

    if clear_button:
        clear_chat()

    if retry_button:
        retry_last()
