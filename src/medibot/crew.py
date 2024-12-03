from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool#, ScrapeWebsiteTool, VisionTool
from pydantic import BaseModel, Field
from typing import List, Optional
from medibot.tools.custom_tool import HumanTool, AvailableSlot, BookSlot, EyeTool
from pydantic import BaseModel, Field
from crewai.tasks.task_output import TaskOutput
# from crewai.tasks.conditional_task import ConditionalTask
import requests
import json

# Loading Human Tools
#human_tools = load_tools(["human"])

# Define a condition function for the conditional task
# If false, the task will be skipped, if true, then execute the task.
def is_doctor_checkup_needed(output: TaskOutput) -> bool:
    print("output.pydantic.doctor_checkup_needed", output)
    return output.pydantic.doctor_checkup_needed

class Preassessment(BaseModel):
    """General practitioner Preassessment output model"""
    #message_to_patient: str = Field(..., description="Comprehensive message to the patient")
    interview_summary: str = Field(..., description="the detailed summary of the patient's input")
    diagnoses: str = Field(..., description="The diagnoses based on your medical knowledge")
    doctor_checkup_needed: bool = Field(..., description="whether the patient to see the doctor urgently")

def general_practitioner_task_callback(output: TaskOutput):
    # Do something after the task is completed
    # Example: Send an email to the manager
    print('###Output###')
    print(output)
    print('###Output raw###')
    # print(output.raw)
    # print(type(output.raw))
    # print(output.interview_summary)
    #print(output.raw.interview_summary)
    #print(json.loads(output.raw).get('interview_summary'))
    # print(output)

    # data = {'patient_id': '160900AAgent', 'description': str(output.pydantic.interview_summary), 'pre_assessment': str(output.pydantic.diagnoses)}
    # headers = {'Content-Type': 'application/json'}

    # response = requests.post('https://main-bvxea6i-5gtrd4rbck7xm.eu-5.platformsh.site/add-request', data=json.dumps(data), headers=headers)
    # print(response.text)

@CrewBase
class MedibotCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def general_practitioner(self) -> Agent:
        return Agent(
            config=self.agents_config['general_practitioner'],
            #tools=[SerperDevTool(), VisionTool(), HumanTool(), EyeTool()], # Example of custom tool, loaded at the beginning of file
            tools=[SerperDevTool(), HumanTool()], # Example of custom tool, loaded at the beginning of file
            verbose=True,
            allow_delegation=True,
        )
    
    @agent
    def appointment_scheduler(self) -> Agent:
        return Agent(
            config=self.agents_config['appointment_scheduler'],
            #tools=[SerperDevTool(), VisionTool(), HumanTool(), EyeTool()], # Example of custom tool, loaded at the beginning of file
            tools=[SerperDevTool(), HumanTool(),AvailableSlot(),BookSlot()], # Example of custom tool, loaded at the beginning of file
            verbose=True,
            allow_delegation=False,
        )

    '''@agent
    def clinic_receptionist(self) -> Agent:
        return Agent(
            config=self.agents_config['clinic_receptionist'],
            #tools=[EyeTool(), AppointmentTool(), VisionTool()],
            tools=[EyeTool()],
            verbose=True,
            allow_delegation=False,
        )'''

    '''@task
    def personal_info_collector(self) -> Task:
        return Task(
            config=self.tasks_config['personal_info_collector'],
            agent=self.clinic_receptionist(),
            #callback=general_practitioner_task_callback

            # condition=is_doctor_checkup_needed
        )'''

    @task
    def general_practitioner_task(self) -> Task:
        return Task(
            config=self.tasks_config['general_practitioner_task'],
            agent=self.general_practitioner(),
            output_pydantic=Preassessment,
            callback=general_practitioner_task_callback,
            # human_input=True
        )
    
    @task
    def appointment_scheduling_task(self) -> Task:
        return Task(
            config=self.tasks_config['appointment_scheduling_task'],
            agent=self.appointment_scheduler(),
            condition=is_doctor_checkup_needed
            # human_input=True
        )

    '''@task
    def clinic_appointment_maker_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['clinic_appointment_maker_task'],
            agent=self.clinic_receptionist(),
            context=[self.general_practitioner_task()],
            #callback=general_practitioner_task_callback

            condition=is_doctor_checkup_needed
        )'''

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=1,
            # process=Process.hierarchical, # In case you want to use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
