import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.marketing_assistant.utils import read_sales_data, analyze_marketing_results
from src.marketing_assistant.logger import logging

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from operator import itemgetter

load_dotenv()
key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key=key, model_name="gpt-3.5-turbo", temperature=0.7)

strategy_template = """
Business Context:
{business_description}

Target Market:
{target_market}

Budget: {budget}

Sales Data:
{sales_data}

Previous Marketing Content:
{marketing_content}

Previous Strategy:
{previous_strategy}

You are an expert marketing strategist. Create a detailed marketing strategy that includes:
1. Key Marketing Channels
2. Content Strategy
3. Budget Allocation
4. Expected ROI
5. Timeline

Format the response as a JSON with the following structure:
{{
    "channels": [
        {{
            "name": "channel name",
            "strategy": "strategy description",
            "budget_percentage": number,
            "expected_roi": "ROI description"
        }}
    ],
    "content_strategy": {{
        "key_themes": [],
        "content_types": [],
        "posting_frequency": ""
    }},
    "timeline": {{
        "month1": "activities",
        "month2": "activities",
        "month3": "activities"
    }}
}}
"""

strategy_prompt = PromptTemplate(
    input_variables=["business_description", "target_market", "budget", "sales_data", "marketing_content", "previous_strategy"],
    template=strategy_template
)

# Create the chains
def create_strategy(inputs):
    return {
        "business_description": inputs["business_description"],
        "target_market": inputs["target_market"],
        "budget": inputs["budget"],
        "sales_data": inputs["sales_data"],
        "marketing_content": inputs["marketing_content"],
        "previous_strategy": inputs["previous_strategy"]
    }

strategy_chain = (
    RunnablePassthrough(create_strategy)
    | strategy_prompt
    | llm
    | (lambda x: {"strategy": x.content})
)

review_template = """
Analyze the following marketing strategy and provide recommendations for improvement:

Strategy:
{strategy}

Provide your analysis in the following format:
1. Strengths
2. Weaknesses
3. Recommendations
"""

review_prompt = PromptTemplate(
    input_variables=["strategy"],
    template=review_template
)

def create_review(inputs):
    return {"strategy": inputs["strategy"]["strategy"]}

review_chain = (
    RunnablePassthrough(create_review)
    | review_prompt
    | llm
    | (lambda x: {"review": x.content})
)

performance_template = """
Analyze the following marketing performance data and provide insights:

Sales Data:
{sales_data}

Marketing Content:
{marketing_content}

Previous Strategy:
{previous_strategy}

Provide analysis in the following format:
1. Performance Overview
2. Key Insights
3. Recommendations for Strategy Adjustment
4. Potential Opportunities
"""

performance_prompt = PromptTemplate(
    input_variables=["sales_data", "marketing_content", "previous_strategy"],
    template=performance_template
)

def create_performance(inputs):
    return {
        "sales_data": inputs["sales_data"],
        "marketing_content": inputs["marketing_content"],
        "previous_strategy": inputs["previous_strategy"]
    }

performance_chain = (
    RunnablePassthrough(create_performance)
    | performance_prompt
    | llm
    | (lambda x: {"performance_analysis": x.content})
)

# Combine the chains
def generate_review_chain(inputs):
    # Run chains in parallel and combine results
    results = {
        "strategy": strategy_chain.invoke(inputs),
        "review": lambda x: review_chain.invoke({"strategy": x["strategy"]["strategy"]}),
        "performance": performance_chain.invoke(inputs)
    }
    return results
