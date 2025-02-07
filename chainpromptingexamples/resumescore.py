from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
import sys
import re

from util import llm


# Graph state
class State(TypedDict):
    resume_text: str
    job_description: str
    ats_score: float
    improvements: str
    final_output: str
    resume_info: str


# Nodes
def extract_resume_details(state: State):
    resume_info = llm.invoke(f"Analyse key skills and experience from this experience:\n{state['resume_text']}")
    return {"resume_info": resume_info.content}

def match_with_job_description(state: State):
    # Compare resume and job description (get match score as a numeric value)
    match_analysis = llm.invoke(
        f"Compare this resume_info with the job description and give an ATS score in percentage like ATS Score: 65% :\nResume: {state['resume_info']}\nJob Description: {state['job_description']}"
    )
    
    # Now, use regex to find a pattern like "Match Score: 90%"
    match_score_str = match_analysis.content  # Example: "Match Score: 90%"
    
    # Regular expression to extract numeric value
    match = re.search(r"ATS Score:\s*(\d+)", match_score_str)
    
    if match:
        # Extract the numeric score and convert it to float
        match_score = float(match.group(1))
    else:
        # If no score is found, set default to 0
        match_score = 0.0
    
    # Return the ats_score
    return {"ats_score": match_score}


def ats_score_check(state: State):
    
    if state["ats_score"] >= 80:  # Changed from 8 to 80 since score is in percentage
        return "Pass"
    return "Fail"

def suggest_improvements(state: State):
    improvements = llm.invoke(f"Based on the job description, suggest improvements to make the resume better. The improvement should be one line:\n"
                              f"Resume: {state['resume_info']}\nJob Description: {state['job_description']}")
    return {"improvements": improvements.content}

def generate_final_output(state: State):
    if "improvements" in state:
        prompt = f"Incorporate the changes as the final resume points basis the improvements suggested\nResume: {state['improvements']}"
    else:
        prompt = f"Format the following resume info as final points:\nResume: {state['resume_info']}"
    final_output = llm.invoke(prompt)
    return {"final_output": final_output.content}


# Create the workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("extract_resume_details", extract_resume_details)
workflow.add_node("match_with_job_description", match_with_job_description)
workflow.add_node("ats_score_check", ats_score_check)
workflow.add_node("suggest_improvements", suggest_improvements)
workflow.add_node("generate_final_output", generate_final_output)

# Add edges (connections between nodes)
workflow.add_edge(START, "extract_resume_details")
workflow.add_edge("extract_resume_details", "match_with_job_description")
workflow.add_conditional_edges(
    "match_with_job_description", 
    ats_score_check,
    # Always go through suggest_improvements regardless of pass/fail
    {"Pass": "suggest_improvements", "Fail": "suggest_improvements"}
)
workflow.add_edge("suggest_improvements", "generate_final_output")
workflow.add_edge("generate_final_output", END)

# Compile the workflow
chain = workflow.compile()

# Input data
resume_text = "--name--\nSpearheaded the development and facilitation of a digital secured lending platform for SME customers, contributing an additional ~Rs 30 Cr annually to the lending portfolio\nDeveloped a guided self-served digital lending interface for end customers reducing the loan sanction turnaround time by 50%\nOrchestrated the flow of entire lead conversion cycle via CRM integration & drop lead calling strategies, boosting conversion rate by 10%\nLed the end-to-end launch of a Mobile Application for assisted onboarding of users by sales team, increasing platform user base by 12%\nExecuted data-driven digital campaigns, resulting in a 50% increase in clicks and a 10% increase in loan sanctions across the products \nManaged and groomed the JIRA product backlog, authored testable and independent user stories, and led a cross-functional agile team in continuous feature development and deployment, ensuring alignment with the product roadmap\nExecuted a thorough multi-channel communication strategy, covering all customer touchpoints to ensure product awareness \nSkilled in creating product requirement documents, wireframes, understanding user journey, data analysis & delivering presentations\nAppreciated in multiple forums for conducting training sessions for various teams, mentored 10+ product team members"
job_description = "What you'll do?\n\nDevelop and drive the product roadmap for Atlan's metadata applications, including but not limited to adapters or connectors, while aligning with business objectives and customer needs.\nImprove customer onboarding and accelerate time-to-value by ensuring metadata applications are easy to adopt, highly functional, and deliver immediate business impact.\nCollaborate with internal stakeholders and customers to gather requirements, translate them into clear product specifications, and prioritize feature development.\nExecute the roadmap through metadata application research, market research, and industry trend analysis.\nWork closely with engineering teams to plan, develop, and deliver high-quality metadata applications on time and to standard.\nChampion the user experience for metadata applications, collaborating with the design team to create intuitive and efficient workflows.\nBuild and maintain strong feedback loops with customers and internal stakeholders (e.g., product and engineering teams) to drive continuous improvement.\nMonitor and analyze application performance, usage data, and customer feedback to identify areas for enhancement.\nEnsure seamless metadata integration with varied sources and readiness of the platform to function as an actual control plane for metadata.\n\nWhat makes you a match?\n\nExperience: Proven experience in product management, particularly with platform or enterprise products. Experience developing data integration products is a significant plus.\nTechnical Skills: Strong technical background and understanding of metadata applications, adapters, APIs, data integration methodologies, and modern data stack tools.\nCustomer-Centric Approach: Deep empathy for customers, with a track record of delivering solutions that improve onboarding, drive adoption, and create measurable value and impact.\nProven experience working with developer-facing products (external and internal) or similar.\nCollaboration: Exceptional communication and collaboration skills, with the ability to work effectively across cross-functional teams and influence stakeholders at all levels.\nAnalytics & Design: Strong analytical and visualization skills, with a focus on user experience and interface design.\nOrganization: Ability to manage multiple projects in a fast-paced environment while maintaining a high level of organization.\nCloud & Metadata Knowledge: Strong understanding of cloud-native architectures, metadata management, and enterprise-grade scalability and security"

# Invoke the workflow
state = chain.invoke({"resume_text": resume_text, "job_description": job_description})

# Display results
print("ATS Score:", state["ats_score"])
if "improvements" in state:
    print("Suggested Improvements:", state["improvements"])
else:
    print("Final Output:", state["final_output"])
