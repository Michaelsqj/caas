import asyncio
import datetime
import os
import platform
import uuid

# ==============================================================================
# ========================= Setup working directory ============================
# ==============================================================================
WORKING_DIRECTORY = os.environ.get("CAMEL_WORKDIR")
date_time_ext=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+f"_{str(uuid.uuid4())[:4]}"
# get current python script filname,
FILENAME=os.path.splitext(os.path.basename(__file__))[0]
WORKING_DIRECTORY = f"{WORKING_DIRECTORY}/{FILENAME}/{date_time_ext}"
CAMEL_LOG_DIR=os.environ.get("CAMEL_LOG_DIR")
CAMEL_LOG_DIR=f"{CAMEL_LOG_DIR}/{FILENAME}/{date_time_ext}"
os.environ.update({
    "CAMEL_WORKDIR": WORKING_DIRECTORY,
    "CAMEL_MODEL_LOG_ENABLED": "true",
    "CAMEL_LOG_DIR": CAMEL_LOG_DIR,
})
WORKSPACE="/Users/qijia/Documents/PumpkinMango1/WORKSPACE"
# create a symbolic link from WORKING_DIRECTORY/workspace to WORKSPACE
os.makedirs(WORKING_DIRECTORY, exist_ok=True)
os.system(f"rm -rf {WORKING_DIRECTORY}/WORKSPACE")
os.system(f"cp -r {WORKSPACE} {WORKING_DIRECTORY}/WORKSPACE")
WORKSPACE=f"{WORKING_DIRECTORY}/WORKSPACE"


from camel.agents.chat_agent import ChatAgent
from camel.logger import get_logger
from camel.messages.base import BaseMessage
from camel.models import BaseModelBackend, ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks.task import Task
from camel.toolkits import (
    AgentCommunicationToolkit,
    AudioAnalysisToolkit,
    ExcelToolkit,
    FileToolkit,
    # GoogleDriveMCPToolkit,
    HumanToolkit,
    HybridBrowserToolkit,
    ImageAnalysisToolkit,
    LinkedInToolkit,
    MarkItDownToolkit,
    NoteTakingToolkit,
    NotionToolkit,
    OpenAIImageToolkit,
    PPTXToolkit,
    RedditToolkit,
    ScreenshotToolkit,
    SearchToolkit,
    SlackToolkit,
    TerminalToolkit,
    ToolkitMessageIntegration,
    TwitterToolkit,
    VideoDownloaderToolkit,
    WebDeployToolkit,
    WhatsAppToolkit,
)
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage
from camel.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
def send_message_to_user(
    message_title: str,
    message_description: str,
    message_attachment: str = "",
) -> str:
    r"""Use this tool to send a tidy message to the user, including a
    short title, a one-sentence description, and an optional attachment.

    This one-way tool keeps the user informed about your progress,
    decisions, or actions. It does not require a response.
    You should use it to:
    - Announce what you are about to do.
      For example:
      message_title="Starting Task"
      message_description="Searching for papers on GUI Agents."
    - Report the result of an action.
      For example:
      message_title="Search Complete"
      message_description="Found 15 relevant papers."
    - Report a created file.
      For example:
      message_title="File Ready"
      message_description="The report is ready for your review."
      message_attachment="report.pdf"
    - State a decision.
      For example:
      message_title="Next Step"
      message_description="Analyzing the top 10 papers."
    - Give a status update during a long-running task.

    Args:
        message_title (str): The title of the message.
        message_description (str): The short description.
        message_attachment (str): The attachment of the message,
            which can be a file path or a URL.

    Returns:
        str: Confirmation that the message was successfully sent.
    """
    print(f"\nAgent Message:\n{message_title} " f"\n{message_description}\n")
    if message_attachment:
        print(message_attachment)
    logger.info(
        f"\nAgent Message:\n{message_title} "
        f"{message_description} {message_attachment}"
    )
    return (
        f"Message successfully sent to user: '{message_title} "
        f"{message_description} {message_attachment}'"
    )
# =============================================================================

model_backend = ModelFactory.create(
    model_platform=ModelPlatformType.AZURE,
    model_type=ModelType.GPT_5_2,
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    url=os.environ.get("AZURE_OPENAI_BASE_URL"),
    api_version=os.environ.get("AZURE_API_VERSION"),
    model_config_dict={
        "stream": False,
    },
)



# =============================================================================
# ============= Toolkit init: Document toolkits + browser toolkit =============
# =============================================================================

# Initialize message integration
message_integration = ToolkitMessageIntegration(
    message_handler=send_message_to_user
)

# Browser toolkit
custom_tools = [
    "browser_open",
    "browser_close",
    "browser_back",
    "browser_forward",
    "browser_click",
    "browser_type",
    "browser_enter",
    "browser_switch_tab",
    "browser_visit_page",
    # "browser_get_som_screenshot",
    "browser_get_page_snapshot"
    "browser_select"
]
web_toolkit_custom = HybridBrowserToolkit(
    headless=False,
    enabled_tools=custom_tools,
    browser_log_to_file=True,
    log_dir=f"{WORKING_DIRECTORY}/browser_log/",
    stealth=True,
    viewport_limit=False,
    cache_dir=f"{WORKING_DIRECTORY}/browser_cache/",
    user_data_dir=f"{WORKING_DIRECTORY}/browser_user_data/",
    cdp_keep_current_page=True,
)

# Document toolkits
# Initialize toolkits
file_toolkit = FileToolkit(working_directory=WORKING_DIRECTORY)
excel_toolkit = ExcelToolkit(working_directory=WORKING_DIRECTORY)
note_toolkit = NoteTakingToolkit(working_directory=WORKING_DIRECTORY)
terminal_toolkit = TerminalToolkit(safe_mode=True, clone_current_env=False)

# Register toolkits with message integration
web_toolkit_custom = message_integration.register_toolkits(
        web_toolkit_custom
)
file_toolkit = message_integration.register_toolkits(
    file_toolkit
)

excel_toolkit = message_integration.register_toolkits(excel_toolkit)
note_toolkit = message_integration.register_toolkits(note_toolkit)
terminal_toolkit = message_integration.register_toolkits(terminal_toolkit)

# Define task prompt
tools = [
    *file_toolkit.get_tools(),
    # HumanToolkit().ask_human_via_console,
    *excel_toolkit.get_tools(),
    *note_toolkit.get_tools(),
    *terminal_toolkit.get_tools(),
    *web_toolkit_custom.get_tools(),
]


# =============================================================================
# ============================ Set system message  ============================
# =============================================================================

system_message=f"""
<role>
You are a Form-Filling & Document Automation Agent. Your primary responsibility
is to complete end-to-end workflows that involve (1) reading and writing
documents, (2) preparing structured data for submission, and (3) filling
online forms including authentication/login steps when required, while
keeping the user informed and producing verifiable outputs.
</role>

<operating_environment>
- System: {platform.system()} ({platform.machine()})
- Working Directory: `{WORKING_DIRECTORY}`. Treat this as the default location
  for generated artifacts (exports, reports, screenshots/logs if available).
- Current Date: {datetime.date.today()}
</operating_environment>

<available_tools_and_how_to_use_them>
You have access to the following capabilities via tools (use them rather than
describing what you would do):

1) Document & File Operations
- FileToolkit: create and write files (HTML/Markdown/JSON/CSV/plain text, etc.)
- ExcelToolkit: read/write spreadsheets and transform tabular data

2) Terminal Operations
- TerminalToolkit (safe_mode enabled): run commands to list and search files, inspect
  outputs, and automate repeatable steps.

3) Notes / Memory
- NoteTakingToolkit: record tasks, decomposition, planning,
  record intermediate findings, so as to maintain an external memory in long horizon.


Important: Only claim you performed an action if you actually executed it via
the available tools. If a required capability (e.g., browser automation) is
not available in the current tools list, request an adjustment.
</available_tools_and_how_to_use_them>

<scope_of_responsibilities>
You must be able to:
- Read documents provided by the user (PDF/Doc/HTML/images where supported),
  extract relevant fields.
- Produce submission-ready artifacts (JSON payloads, CSVs, filled templates,
  HTML summaries, spreadsheets).
- Fill online forms and handle login flows where needed (username/password,
  OAuth-like flows, MFA/OTP), while minimizing exposure of secrets.
- Track what was submitted, when, and which source data was used, and write a
  clear local audit trail in the working directory (e.g., `submission_log.txt`
  or `submission_receipt.json`).
- Plan and decompose tasks, and track the progress of multi-step workflows using notes.
- You must inform the user every step you take using the tool concisely. 

Reliability:
- Validate outputs (e.g., confirm file exists, check folder contents, schema consistency, required
  fields present) using the terminal toolkit where appropriate.
- If a workflow has irreversible steps (final submission, payment, deletes),
  ask the user for explicit confirmation right before executing.
</scope_of_responsibilities>

<execution_workflow>
For each task, follow this workflow:

1) Clarify & Plan
- Restate the goal and list required inputs (documents, target URL, account
  state, required fields).

2) Extract & Prepare Data
- Use ExcelToolkit / FileToolkit to extract and structure
  the user data.
- Store clean intermediate artifacts in `{WORKING_DIRECTORY}` (e.g.,
  `form_fields.json`, `normalized_profile.csv`).
- Record assumptions and mapping decisions in notes.

3) Perform Form Interaction
- Navigate, login, complete every single form fields, upload documents, and reach the final
  review step.
- Never submit or pay.
- After completion, look for preview or print page option to convert the filled form results to PDF
  and save to {WORKING_DIRECTORY} for verification.
- If necessary, pause the form filling, and search and retrieve missing info from the {WORKING_DIRECTORY}.

4) Produce Deliverables
- Write a concise Markdown summary: what data used, what was submitted,
  any remaining actions (note, only if the stopped because absolutely cannot skip and proceed) and links/paths to generated artifacts.
  This should be informative for humans or other agents or your own future reference.
- Output paths must be absolute or clearly relative to `{WORKING_DIRECTORY}`.
</execution_workflow>

<communication_style>
- Be brief, procedural, and explicit about what you will do next.
- Prefer checklists and numbered steps.
</communication_style>

<efficiency_guidelines>
- Minimize the turn of model request by using parallel tool calls where possible. 
- For form-filling, you can analyze the whole page at once, and fill in all fields you can find in one single step, using multiple tool calls during form filling.
</efficiency_guidelines>

<failure_handling>
If something fails:
- Record the exact error message/context in notes.
- Propose the smallest corrective action.
- Retry once after fixing. If still failing, ask the human with a clear prompt
  including what you need from them.
</failure_handling>
"""

agent = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Form-filling Agent",
        content=system_message,
    ),
    model=model_backend,
    tools=tools,
    step_timeout=None,
    prune_tool_calls_from_memory=True,
)

TASK_PROMPT=f"""
You job is filling the college application online form using information from the documents in workspace:{WORKSPACE}.

Your job includes:
-. Read and extract website URL, username, password from workspace folder. You need to find the info from files in the {WORKSPACE}.
-. You need to login to the website using the username and password.
-. You need to explore the website, understand the page and fill in any entries that you have information from docs in {WORKSPACE}. Try looking around, and click links/buttons to explore.
-. Retrieve the info needed if necessary from the documents in the {WORKSPACE}.
-. Record any information that is required in the website but you cannot find in {WORKSPACE} in a note in {WORKING_DIRECTORY}.
-. Tell me which places and fields on the website you have found to fill in
-. Fill in the online wesite form per the info from the documents you found/ generated in the workspace or the generated one in {WORKING_DIRECTORY}.

Prohibited behaviors:
- Do not change any workspace file in place. always create a new one if you need to create or modify a file.
- Never click submit or pay button or any dangerou and irreversible action.
- You are allowed to click any harmless buttons like `continue` button to proceed to the next step of the form filling.


Note: 
- the browser page may take some time to load or respond, if nothing happens after your action, check the browser status in 
    next iteration or after other tasks, check for max 5 times before you give up return.
- You are allowed to read and write files under {WORKING_DIRECTORY}.
- Don't ask for my permission during your execution, just inform me of each step clearly, and try to fill in any field that you can, 
  until there are no more fields to fill in or you reach the final review page.
- During form filling, try to be as efficient as possible! You can analyze the whole page at once, and
  fill in any fillable fields on the current page in one single step, rather than filling in one field at a time.
- Although you may not find exactly same field names in the documents, try to understand and find the correct info with just reasonable mapping/approximation.
- **Important**: If you find any inconsistency between already filled fields and the documents, always trust the documents and overwrite the fields with correct info from the documents.
    Correct any field filled with wrong info mismatched with the document. including name , address these basic information.
- **Important**: If you need to exit, explictly tells me the reason that you cannot proceed of skip, or just confirm that you have finished the task.
"""

async def main() -> None:
    try:
        response = await agent.astep(TASK_PROMPT)
        print("Task:", TASK_PROMPT)
        print("\nResponse from agent:")
        print(response.msgs[0].content if response.msgs else "<no response>")
    finally:
        # Ensure browser is closed properly
        print("\nClosing browser...")
        await web_toolkit_custom.browser_close()
        print("Browser closed successfully.")


if __name__ == "__main__":
    asyncio.run(main())