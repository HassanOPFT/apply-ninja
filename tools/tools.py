from .linkedin_tools_old import (
    check_linkedin_login,
    login_to_linkedin,
    navigate_to_job,
    click_easy_apply,
    fill_phone_number,
    get_application_progress,
    get_modal_header_text,
    wait_for_easy_apply_modal,
    close_easy_apply_modal
)
from .browser_tools import (
    initialize_browser,
    get_page,
    wait_for_selector,
    navigate_to,
    fill_field,
    click,
    close_browser,
    get_page_html
)

apply_ninja_tools = [
    # Browser tools
    initialize_browser,
    get_page,
    wait_for_selector,
    navigate_to,
    fill_field,
    click,
    close_browser,
    get_page_html,
    
    # LinkedIn specific tools
    check_linkedin_login,
    login_to_linkedin,
    navigate_to_job,
    click_easy_apply,
    fill_phone_number,
    get_application_progress,
    get_modal_header_text,
    wait_for_easy_apply_modal,
    close_easy_apply_modal
]