import streamlit as st
import json
from src.marketing_assistant.MarketingGenerator import generate_review_chain
from langchain_community.callbacks.manager import get_openai_callback
import pandas as pd
from src.marketing_assistant.utils import read_file, read_sales_data, analyze_marketing_results

st.title("Marketing Division Generator & Analyzer 🚀")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Generate Strategy", "PDF & CSV Analyzer"])

with tab1:
    with st.form("marketing_inputs"):
        business_description = st.text_area(
            "Describe your business",
            placeholder="E.g., We are a B2B SaaS company providing AI-powered analytics..."
        )
        
        target_market = st.text_area(
            "Describe your target market",
            placeholder="E.g., Small to medium-sized businesses in the manufacturing sector..."
        )
        
        budget = st.number_input(
            "Monthly Marketing Budget ($)",
            min_value=100,
            max_value=1000000,
            value=1000
        )
        
        # Add file upload options
        marketing_pdf = st.file_uploader("Upload previous marketing materials (PDF)", type=["pdf"])
        sales_data = st.file_uploader("Upload sales data (CSV)", type=["csv"])
        
        submit = st.form_submit_button("Generate Strategy")
        
        if submit:
            with st.spinner("Analyzing data and generating strategy..."):
                try:
                    # Process uploaded files
                    marketing_content = read_file(marketing_pdf) if marketing_pdf else ""
                    sales_summary = read_sales_data(sales_data) if sales_data else {}
                    
                    # Generate strategy with additional context
                    with get_openai_callback() as cb:
                        input_data = {
                            "business_description": business_description,
                            "target_market": target_market,
                            "budget": budget,
                            "sales_data": json.dumps(sales_summary),
                            "marketing_content": marketing_content,
                            "previous_strategy": ""
                        }
                        
                        response = generate_review_chain(input_data)
                        
                        # Display strategy
                        if "strategy" in response:
                            st.write("### Marketing Strategy")
                            strategy_dict = json.loads(response["strategy"]["strategy"])
                            
                            # Display Channels table with specific columns and hide the index
                            st.write("#### Marketing Channels")
                            channels_df = pd.DataFrame({
                                'Channel Name': [channel['name'] for channel in strategy_dict["channels"]],
                                'Strategy': [channel['strategy'] for channel in strategy_dict["channels"]],
                                'Budget Percentage': [channel['budget_percentage'] for channel in strategy_dict["channels"]],
                                'Expected ROI': [channel['expected_roi'] for channel in strategy_dict["channels"]]
                            })
                            st.dataframe(channels_df, hide_index=True, use_container_width=True)
                            
                            # Display Content Strategy
                            st.write("#### Content Strategy")
                            content_df = pd.DataFrame({
                                'Key Themes': strategy_dict["content_strategy"]["key_themes"],
                                'Content Types': strategy_dict["content_strategy"]["content_types"]
                            })
                            st.dataframe(content_df, hide_index=True, use_container_width=True)
                            
                            st.write("Posting Frequency:", strategy_dict["content_strategy"]["posting_frequency"])
                            
                            # Display Timeline
                            st.write("#### Timeline")
                            timeline_df = pd.DataFrame({
                                'Month': list(strategy_dict["timeline"].keys()),
                                'Activities': list(strategy_dict["timeline"].values())
                            })
                            st.dataframe(timeline_df, hide_index=True, use_container_width=True)
                        
                        # Display review
                        # if "review" in response:
                        #     st.write("### Strategy Review")
                        #     st.write(response["review"]["review"])
                        
                        # Display performance analysis
                        if "performance" in response and sales_summary:
                            st.write("### Performance Insights")
                            st.write(response["performance"]["performance_analysis"])
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with tab2:
    st.write("### PDF & CSV Analysis")
    
    uploaded_files = st.file_uploader(
        "Upload marketing materials and sales data",
        type=["pdf", "csv"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith('.pdf'):
                content = read_file(file)
                analysis = analyze_marketing_results(content)
                st.write(f"**Analysis for {file.name}:**")
                st.json(analysis)
            elif file.name.endswith('.csv'):
                sales_data = read_sales_data(file)
                st.write(f"**Sales Analysis for {file.name}:**")
                st.json(sales_data)