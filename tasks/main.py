import sys
import os
import streamlit as st
from utils.voice_utils import record_and_transcribe
from utils.vision_utils import PoseDetector, wrists_above_head
import re
import time
import cv2

# Initialize session state variables
if "physical_tasks_results" not in st.session_state:
    st.session_state.physical_tasks_results = []

if "linguistic_tasks_results" not in st.session_state:
    st.session_state.linguistic_tasks_results = []

if "cognitive_tasks_results" not in st.session_state:
    st.session_state.cognitive_tasks_results = []

try:
    from utils.report_generator import ReportGenerator

    report_generator = ReportGenerator()
except ImportError as e:
    print(f"Warning: Could not import ReportGenerator: {str(e)}")
    report_generator = None

# Import all task modules
from linguistic_0_say_mama import task as linguistic_task_0
from linguistic_1_apple import task as linguistic_task_1
from linguistic_2_rhyme_cat import task as linguistic_task_2
from linguistic_3_fill_blank import task as linguistic_task_3
from linguistic_4_sentence_sun import task as linguistic_task_4
from linguistic_5_story_kite import task as linguistic_task_5

from physical_0_raise_hands import task as physical_task_0
from physical_1_one_leg import task as physical_task_1
from physical_2_turn_around import task as physical_task_2
from physical_3_stand_still import task as physical_task_3
from physical_4_frog_jump import task as physical_task_4
from physical_5_kangaroo_jump import task as physical_task_5

from intelligence_tasks import INTELLIGENCE_QUESTIONS


# Custom CSS for better contrast and visibility
def load_css():
    st.markdown("""
    <style>
        /* Modern gradient background */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }

        /* Card styling */
        .question-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }

        /* Text styling */
        h1 {
            color: white !important;
            text-align: center;
            font-size: 2.5rem !important;
            margin-bottom: 2rem !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        h2, h3, h4 {
            color: #2c3e50 !important;
            text-align: center;
            margin: 1rem 0 !important;
        }

        p {
            color: #2c3e50 !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(45deg, #4CAF50 30%, #45a049 90%) !important;
            color: white !important;
            border-radius: 25px !important;
            padding: 0.6rem 2rem !important;
            font-weight: 600 !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
            width: 100%;
            margin: 0.5rem 0;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }

        /* Radio button styling */
        .stRadio > div {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }

        .stRadio > div > label {
            color: #2c3e50 !important;
            font-size: 1.1rem !important;
            padding: 0.5rem !important;
            cursor: pointer;
        }

        /* Success/Error message styling */
        .stSuccess, .stError {
            padding: 1rem !important;
            border-radius: 10px !important;
            margin: 1rem 0 !important;
        }

        /* Image styling */
        .stImage > img {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* Metrics styling */
        .stMetric {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* Progress bar styling */
        .stProgress > div > div {
            background: linear-gradient(45deg, #4CAF50 30%, #45a049 90%) !important;
        }

        /* Score display styling */
        .score-display {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* Task category badges */
        .task-badge {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            margin: 0.3rem;
            text-align: center;
        }

        .physical-badge {
            background: linear-gradient(45deg, #FF6B6B 30%, #FF8E8E 90%);
        }

        .linguistic-badge {
            background: linear-gradient(45deg, #4ECDC4 30%, #45B7AF 90%);
        }

        .intelligence-badge {
            background: linear-gradient(45deg, #9B59B6 30%, #8E44AD 90%);
        }
    </style>
    """, unsafe_allow_html=True)


# Set page config
st.set_page_config(page_title="Child Development Assessment", layout="centered")

# Load CSS
load_css()

# Initialize session state
if 'age_group' not in st.session_state:
    st.session_state.age_group = None
if 'current_task' not in st.session_state:
    st.session_state.current_task = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'user_info' not in st.session_state:
    st.session_state.user_info = {
        'child_name': '',
        'child_age': '',
        'child_sex': '',
        'parent_name': '',
        'parent_phone': '',
        'parent_email': '',
        'location': ''
    }


def select_age_group():
    st.title("Child Development Assessment")

    # Add a welcoming header with emoji
    st.markdown("""
        <div class='question-card'>
            <h2>👶 Welcome to Born AI Assessment!</h2>
            <p style='text-align: center;'>
                Let's discover your child's development milestones through fun and interactive tasks.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # User Information Form
    st.markdown("""
        <div class='question-card'>
            <h3>📋 Personal Information</h3>
            <p style='text-align: center; color: #666;'>
                Please fill in the following details to begin the assessment
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("user_info_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4>Child Information</h4>", unsafe_allow_html=True)
            child_name = st.text_input("Child's Name",
                                       value=st.session_state.user_info['child_name'],
                                       placeholder="Enter child's full name")
            child_age_years = st.number_input("Child's Age (Years)",
                                              min_value=0, max_value=6,
                                              value=int(st.session_state.user_info['child_age']) if
                                              st.session_state.user_info['child_age'].isdigit() else 0)
            child_age_months = st.number_input("Child's Age (Months)",
                                               min_value=0, max_value=11,
                                               value=0)
            child_sex = st.selectbox("Child's Sex",
                                     options=['Select', 'Male', 'Female', 'Other'],
                                     index=0 if not st.session_state.user_info['child_sex'] else
                                     ['Select', 'Male', 'Female', 'Other'].index(
                                         st.session_state.user_info['child_sex']))

        with col2:
            st.markdown("<h4>Parent/Guardian Information</h4>", unsafe_allow_html=True)
            parent_name = st.text_input("Parent's Name",
                                        value=st.session_state.user_info['parent_name'],
                                        placeholder="Enter parent's full name")
            parent_phone = st.text_input("Phone Number",
                                         value=st.session_state.user_info['parent_phone'],
                                         placeholder="Enter contact number")
            parent_email = st.text_input("Email Address",
                                         value=st.session_state.user_info['parent_email'],
                                         placeholder="Enter email address")
            location = st.text_input("Location",
                                     value=st.session_state.user_info['location'],
                                     placeholder="City, Country")

        submitted = st.form_submit_button("Save Information")
        if submitted:
            # Validate inputs
            if not child_name or not parent_name or not parent_phone or child_sex == 'Select':
                st.error("Please fill in all required fields.")
                return

            # Store user information in session state
            st.session_state.user_info.update({
                'child_name': child_name,
                'child_age': f"{child_age_years}.{child_age_months}",
                'child_sex': child_sex,
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_email': parent_email,
                'location': location
            })
            st.success("Information saved successfully!")

    if all([st.session_state.user_info['child_name'],
            st.session_state.user_info['child_sex'] != 'Select',
            st.session_state.user_info['parent_name'],
            st.session_state.user_info['parent_phone']]):

        # Create age group selection with improved styling
        st.markdown("""
            <div class='question-card'>
                <h3>Select Your Child's Age Group</h3>
                <p style='text-align: center; color: #666;'>
                    Choose the appropriate age range to begin the assessment
                </p>
            </div>
        """, unsafe_allow_html=True)

        age_groups = ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6"]
        col1, col2 = st.columns([3, 1])

        with col1:
            selected = st.radio("", age_groups, horizontal=True,
                                help="Select the age group that best matches your child's current age")

        st.markdown("""
            <div class='question-card'>
                <p style='text-align: center; margin-bottom: 1rem;'>
                    The assessment includes:
                </p>
                <div style='display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
                    <span class='task-badge physical-badge'>Physical Tasks</span>
                    <span class='task-badge linguistic-badge'>Linguistic Tasks</span>
                    <span class='task-badge intelligence-badge'>Intelligence Tasks</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Centered button container
        st.markdown("""
            <div style='display: flex; justify-content: center; margin-top: 2rem;'>
        """, unsafe_allow_html=True)

        if st.button("🎯 Start Assessment", help="Click to begin the assessment"):
            st.session_state.age_group = selected
            st.session_state.current_task = 1
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def perform_physical_task():
    st.title("Physical Development Task")

    # Progress indicator
    st.markdown("""
        <div style='text-align: center'>
            <div class='task-badge physical-badge'>Task 1 of 3</div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
            <div class='question-card'>
                <h3>🏃‍♂️ Physical Activity Challenge</h3>
                <p style='text-align: center; color: #666;'>
                    Let's see how well your child can perform this fun physical task!
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Task execution container
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)

        physical_tasks = {
            "0-1": lambda: run_physical_task(0, physical_task_0, "Raise Hands"),
            "1-2": lambda: run_physical_task(1, physical_task_1, "Stand on One Leg"),
            "2-3": lambda: run_physical_task(2, physical_task_2, "Turn Around"),
            "3-4": lambda: run_physical_task(3, physical_task_3, "Stand Still"),
            "4-5": lambda: run_physical_task(4, physical_task_4, "Frog Jump"),
            "5-6": lambda: run_physical_task(5, physical_task_5, "Kangaroo Jump")
        }

        # Timer display
        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("""
                <div style='background: #f8f9fa; padding: 1rem; border-radius: 10px; text-align: center;'>
                    <p style='margin: 0; color: #666;'>Time Limit</p>
                    <h3 style='margin: 0; color: #2c3e50;'>15s</h3>
                </div>
            """, unsafe_allow_html=True)

        task_func = physical_tasks.get(st.session_state.age_group)
        if task_func:
            score = task_func()
            st.session_state.scores['physical'] = score if score else 0

        st.markdown("</div>", unsafe_allow_html=True)

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again"):
                st.rerun()
        with col2:
            if st.button("Next Task →"):
                st.session_state.current_task = 2
                st.rerun()


def perform_linguistic_task():
    st.title("Language Development Task")

    # Progress indicator
    st.markdown("""
        <div style='text-align: center'>
            <div class='task-badge linguistic-badge'>Task 2 of 3</div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
            <div class='question-card'>
                <h3>🗣️ Language Skills Challenge</h3>
                <p style='text-align: center; color: #666;'>
                    Time to practice speaking and communication skills!
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Task execution container
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)

        linguistic_tasks = {
            "0-1": lambda: run_linguistic_task(0, linguistic_task_0, "Say Mama"),
            "1-2": lambda: run_linguistic_task(1, linguistic_task_1, "Identify Apple"),
            "2-3": lambda: run_linguistic_task(2, linguistic_task_2, "Rhyme with Cat"),
            "3-4": lambda: run_linguistic_task(3, linguistic_task_3, "Fill in the Blank"),
            "4-5": lambda: run_linguistic_task(4, linguistic_task_4, "Make Sun Sentence"),
            "5-6": lambda: run_linguistic_task(5, linguistic_task_5, "Tell Kite Story")
        }

        task_func = linguistic_tasks.get(st.session_state.age_group)
        if task_func:
            st.markdown("""
                <div style='background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <p style='margin: 0; color: #666; text-align: center;'>
                        Click the microphone button and speak clearly 🎤
                    </p>
                </div>
            """, unsafe_allow_html=True)

            score = task_func()
            st.session_state.scores['linguistic'] = score if score else 0

        st.markdown("</div>", unsafe_allow_html=True)

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again"):
                st.rerun()
        with col2:
            if st.button("Next Task →"):
                st.session_state.current_task = 3
                st.rerun()


def ask_intelligence_questions():
    st.title("Cognitive Development Assessment")

    # Progress indicator
    st.markdown("""
        <div style='text-align: center'>
            <div class='task-badge intelligence-badge'>Task 3 of 3</div>
        </div>
    """, unsafe_allow_html=True)

    age_questions = INTELLIGENCE_QUESTIONS.get(st.session_state.age_group, {})
    categories = list(age_questions.keys())

    if 'intelligence_answers' not in st.session_state:
        st.session_state.intelligence_answers = {cat: None for cat in categories}

    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0

    current_category = categories[st.session_state.current_question]
    question_data = age_questions[current_category]

    # Question progress
    progress = (st.session_state.current_question + 1) / len(categories)
    st.progress(progress)
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <p style='color: #666;'>Question {st.session_state.current_question + 1} of {len(categories)}</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
            <div class='question-card'>
                <h3>🧩 Cognitive Skills Assessment</h3>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='question-card'>", unsafe_allow_html=True)

        # Category badge
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <div class='task-badge intelligence-badge'>
                    {current_category.capitalize()} Skills
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Display the question image if available
        if 'image' in question_data:
            image_path = os.path.join("tasks", "assets", question_data['image'])
            try:
                st.image(image_path, use_column_width=True, caption=question_data.get('image_caption', ''))
            except:
                st.warning(
                    f"Image {question_data['image']} not found. Please ensure all required images are in the assets folder.")

        # Question prompt with enhanced styling
        st.markdown(f"""
            <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <p style='text-align: center; font-size: 1.3rem; margin: 0; color: #2c3e50;'>
                    {question_data['prompt']}
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Handle different interaction types
        if question_data['interaction'] == 'tap':
            # Enhanced radio button styling for options
            st.markdown("""
                <p style='text-align: center; color: #666; margin-bottom: 1rem;'>
                    Select your answer:
                </p>
            """, unsafe_allow_html=True)

            answer = st.radio("", question_data['options'],
                              key=f"intel_{current_category}",
                              horizontal=True if len(question_data['options']) <= 3 else False)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Submit Answer", key="submit_answer", use_container_width=True):
                    st.session_state.intelligence_answers[current_category] = answer

                    # Update the task result
                    task_name = f"{current_category.capitalize()} Skills Assessment"
                    score = process_intelligence_task(
                        st.session_state.age_group,
                        current_category,
                        answer,
                        task_name
                    )

                    if 'correct' in question_data:
                        is_correct = (answer == question_data['correct'])
                        if is_correct:
                            st.success("🎉 Correct! Well done!")
                            st.balloons()
                        else:
                            st.error(f"The correct answer was: {question_data['correct']}")
                    else:
                        st.success("Response recorded!")

                    time.sleep(1)  # Short pause for feedback
                    if st.session_state.current_question < len(categories) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.current_task = 4
                        st.rerun()

        elif question_data['interaction'] in ['draw', 'paint', 'decorate']:
            # Enhanced UI for creative activities
            st.markdown("""
                <p style='text-align: center; color: #666; margin-bottom: 1rem;'>
                    Choose your creative tool:
                </p>
            """, unsafe_allow_html=True)

            selected = st.radio("", question_data['options'], horizontal=True)

            # Simple drawing area simulation
            st.markdown("""
                <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; text-align: center;'>
                    <p style='color: #666;'>Drawing area will be implemented here</p>
                </div>
            """, unsafe_allow_html=True)

            st.session_state.intelligence_answers[current_category] = selected

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Submit Creation", key="submit_creative", use_container_width=True):
                    # Update the task result
                    task_name = f"{current_category.capitalize()} Creative Assessment"
                    score = process_intelligence_task(
                        st.session_state.age_group,
                        current_category,
                        selected,
                        task_name
                    )

                    st.success("Great job on your creative work! 🎨")
                    time.sleep(1)
                    if st.session_state.current_question < len(categories) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.current_task = 4
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Navigation hint
        if st.session_state.current_question < len(categories) - 1:
            st.markdown("""
                <div style='text-align: center; margin-top: 1rem;'>
                    <p style='color: #666;'>Submit your answer to move to the next question</p>
                </div>
            """, unsafe_allow_html=True)


def calculate_total_score():
    """Calculate the correct total score and percentage"""
    total_completed = 0
    total_tasks = 0

    # Count physical tasks
    if st.session_state.physical_tasks_results:
        total_tasks += 1
        if any(task.get('completed', False) for task in st.session_state.physical_tasks_results):
            total_completed += 1

    # Count linguistic tasks
    if st.session_state.linguistic_tasks_results:
        total_tasks += 1
        if any(task.get('completed', False) for task in st.session_state.linguistic_tasks_results):
            total_completed += 1

    # Count cognitive tasks (intelligence questions)
    if st.session_state.cognitive_tasks_results:
        for task in st.session_state.cognitive_tasks_results:
            total_tasks += 1
            if task.get('completed', False):
                total_completed += 1

    return total_completed, total_tasks


def generate_pdf_report():
    from fpdf import FPDF
    import tempfile
    import os

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Born AI Development Assessment Report', 0, 1, 'C')
            self.ln(10)

    pdf = PDF()
    pdf.add_page()

    # Add report header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Assessment Date: {time.strftime('%B %d, %Y')}", 0, 1)
    pdf.ln(5)

    # Add child information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Child Information:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Name: {st.session_state.user_info['child_name']}", 0, 1)
    pdf.cell(0, 10, f"Age: {st.session_state.user_info['child_age']} years", 0, 1)
    pdf.cell(0, 10, f"Sex: {st.session_state.user_info['child_sex']}", 0, 1)
    pdf.ln(5)

    # Add parent information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Parent/Guardian Information:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Name: {st.session_state.user_info['parent_name']}", 0, 1)
    pdf.cell(0, 10, f"Contact: {st.session_state.user_info['parent_phone']}", 0, 1)
    pdf.cell(0, 10, f"Email: {st.session_state.user_info['parent_email']}", 0, 1)
    pdf.cell(0, 10, f"Location: {st.session_state.user_info['location']}", 0, 1)
    pdf.ln(10)

    # Add assessment results with correct calculation
    total_completed, total_tasks = calculate_total_score()
    score_percentage = (total_completed / total_tasks * 100) if total_tasks > 0 else 0

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Assessment Results', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Overall Score: {score_percentage:.0f}% ({total_completed}/{total_tasks})", 0, 1)
    pdf.ln(5)

    # Add detailed results
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Detailed Results:', 0, 1)
    pdf.set_font('Arial', '', 12)

    if st.session_state.physical_tasks_results:
        completed = any(task.get('completed', False) for task in st.session_state.physical_tasks_results)
        result = "Successfully completed" if completed else "Needs improvement"
        pdf.cell(0, 10, f"Physical Development: {result}", 0, 1)

    if st.session_state.linguistic_tasks_results:
        completed = any(task.get('completed', False) for task in st.session_state.linguistic_tasks_results)
        result = "Successfully completed" if completed else "Needs improvement"
        pdf.cell(0, 10, f"Language Development: {result}", 0, 1)

    # Add intelligence results
    if st.session_state.cognitive_tasks_results:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Cognitive Skills Results:', 0, 1)
        pdf.set_font('Arial', '', 12)
        for task in st.session_state.cognitive_tasks_results:
            status = "Completed" if task.get('completed', False) else "Incomplete"
            pdf.cell(0, 10, f"- {task.get('task_name', 'Unknown Task')}: {status}", 0, 1)

        # Add recommendations
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations:', 0, 1)
    pdf.set_font('Arial', '', 12)

    if score_percentage >= 80:
        pdf.cell(0, 10, "Excellent development progress! Continue with age-appropriate activities.", 0, 1)
    elif score_percentage >= 60:
        pdf.cell(0, 10, "Good development with some areas for improvement.", 0, 1)
        pdf.cell(0, 10, "Consider additional practice in challenging areas.", 0, 1)
    else:
        pdf.cell(0, 10, "Consider consulting with a child development specialist.", 0, 1)
        pdf.cell(0, 10, "Focus on activities that support developmental milestones.", 0, 1)

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)

    return temp_file.name

def generate_ai_report_from_pdf(pdf_path):
    from utils.report_generator import AIReportGenerator  # adjust path if needed

    try:
        generator = AIReportGenerator()
        success, report_content, metadata = generator.process_pdf_to_ai_report(pdf_path)

        if not success:
            st.error(f"❌ AI Report Generation Failed: {report_content}")
            return None

        child_name = st.session_state.user_info.get("child_name", "Unknown")
        saved_path = generator.save_ai_report(report_content, child_name)
        return saved_path, report_content

    except Exception as e:
        st.error(f"🔥 Error generating AI report: {str(e)}")
        return None, None


import streamlit as st
from datetime import datetime
import json


def show_results():
    st.title("🎉 Comprehensive Development Assessment")

    total_completed, total_tasks = calculate_total_score()
    score_percentage = (total_completed / total_tasks * 100) if total_tasks > 0 else 0

    # Enhanced header with child info
    child_name = st.session_state.user_info['child_name']
    child_age = st.session_state.user_info.get('child_age', 'N/A')

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #2c3e50; margin-bottom: 0.5rem;'>🌟 Assessment Complete for {child_name}</h2>
            <p style='color: #7f8c8d; font-size: 1.1rem; margin: 0;'>Age: {child_age} years • Assessment Date: {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    """, unsafe_allow_html=True)

    # Generate general assessment report first
    pdf_path = generate_pdf_report()

    # Generate AI report and get analysis
    with st.spinner("🧠 Generating comprehensive AI analysis..."):
        ai_report_path, ai_report_content, analysis_metadata = generate_enhanced_ai_report_from_pdf(pdf_path)

    # Parse analysis metadata for visualization
    domain_scores = parse_domain_scores(ai_report_content, analysis_metadata)

    # Overall score display
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;'>
            <h2 style='margin: 0 0 1rem 0; font-size: 2.5rem;'>{score_percentage:.1f}%</h2>
            <h3 style='margin: 0; font-size: 1.5rem;'>Overall Assessment Score</h3>
        </div>
    """, unsafe_allow_html=True)

    # AI-Powered Insights Section
    if ai_report_content:
        st.markdown("## 🧠 AI-Powered Developmental Analysis")

        # Parse and display structured AI content
        display_ai_insights(ai_report_content)

        # Recommendations section
        st.markdown("## 🎯 Personalized Recommendations")
        display_recommendations(ai_report_content, domain_scores)

    # Create combined PDF with both general assessment and AI report
    with st.spinner("📄 Creating combined assessment report..."):
        # Read the original PDF
        with open(pdf_path, "rb") as original_pdf:
            original_pdf_data = original_pdf.read()

        # Create combined PDF data by merging original PDF with AI content
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO
        import PyPDF2

        # Create a new PDF with AI content
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add AI report content to the story with markdown parsing
        if ai_report_content:
            import re

            story.append(Paragraph("<b>AI-Powered Developmental Analysis</b>", styles['Heading1']))
            story.append(Spacer(1, 12))

            # Process markdown content line by line
            lines = ai_report_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 6))
                    continue

                # Handle headers
                if line.startswith('### '):
                    header_text = line[4:].strip()
                    story.append(Paragraph(f"<b>{header_text}</b>", styles['Heading3']))
                    story.append(Spacer(1, 8))
                elif line.startswith('## '):
                    header_text = line[3:].strip()
                    story.append(Paragraph(f"<b>{header_text}</b>", styles['Heading2']))
                    story.append(Spacer(1, 10))
                elif line.startswith('# '):
                    header_text = line[2:].strip()
                    story.append(Paragraph(f"<b>{header_text}</b>", styles['Heading1']))
                    story.append(Spacer(1, 12))

                # Handle bullet points
                elif line.startswith('- ') or line.startswith('* '):
                    bullet_text = line[2:].strip()
                    # Convert markdown formatting within bullet points
                    bullet_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', bullet_text)
                    bullet_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', bullet_text)
                    story.append(Paragraph(f"• {bullet_text}", styles['Normal']))
                    story.append(Spacer(1, 3))

                # Handle numbered lists
                elif re.match(r'^\d+\. ', line):
                    list_text = re.sub(r'^\d+\. ', '', line)
                    # Convert markdown formatting within list items
                    list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                    list_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', list_text)
                    story.append(Paragraph(list_text, styles['Normal']))
                    story.append(Spacer(1, 3))

                # Handle regular paragraphs
                else:
                    # Convert markdown formatting to HTML
                    formatted_text = line
                    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_text)  # Bold
                    formatted_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_text)  # Italic
                    formatted_text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', formatted_text)  # Code

                    story.append(Paragraph(formatted_text, styles['Normal']))
                    story.append(Spacer(1, 6))

        doc.build(story)
        ai_pdf_data = buffer.getvalue()
        buffer.close()

        # Combine both PDFs
        combined_buffer = BytesIO()
        pdf_writer = PyPDF2.PdfWriter()

        # Add original PDF pages
        original_reader = PyPDF2.PdfReader(BytesIO(original_pdf_data))
        for page in original_reader.pages:
            pdf_writer.add_page(page)

        # Add AI report pages
        ai_reader = PyPDF2.PdfReader(BytesIO(ai_pdf_data))
        for page in ai_reader.pages:
            pdf_writer.add_page(page)

        pdf_writer.write(combined_buffer)
        combined_pdf_data = combined_buffer.getvalue()
        combined_buffer.close()

    # Single combined report download section
    st.markdown("## 📄 Download Your Complete Report")

    # Center the download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📄 Download Complete Assessment Report (PDF)",
            data=combined_pdf_data,
            file_name=f"complete_assessment_report_{child_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Complete report including general assessment and AI analysis"
        )

    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def display_ai_insights(ai_content):
    """Display structured AI insights."""
    # Parse markdown sections from AI content
    sections = parse_ai_sections(ai_content)

    # Display in expandable sections
    for section_title, content in sections.items():
        with st.expander(f"📋 {section_title}", expanded=(section_title == "Executive Summary")):
            st.markdown(content)


def display_recommendations(ai_content, domain_scores):
    """Display personalized recommendations."""
    # Extract recommendations from AI content or generate based on scores
    recommendations = extract_recommendations(ai_content, domain_scores)

    for rec in recommendations:
        priority_color = {
            'High': '#e74c3c',
            'Medium': '#f39c12',
            'Low': '#27ae60'
        }.get(rec.get('priority', 'Medium'), '#3498db')

        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 1rem 0;
                        border-left: 4px solid {priority_color};'>
                <h4 style='color: #2c3e50; margin: 0 0 1rem 0;'>
                    🎯 {rec.get('domain', 'General')} - 
                    <span style='color: {priority_color};'>{rec.get('priority', 'Medium')} Priority</span>
                </h4>
                <p style='margin: 0.5rem 0;'><strong>Activity:</strong> {rec.get('activity', 'No specific activity')}</p>
                <p style='margin: 0.5rem 0;'><strong>Frequency:</strong> {rec.get('frequency', 'As needed')}</p>
                <p style='margin: 0.5rem 0;'><strong>Goal:</strong> {rec.get('goal', 'General improvement')}</p>
            </div>
        """, unsafe_allow_html=True)


def parse_domain_scores(ai_content, metadata):
    """Parse domain scores from AI content or generate from session state."""
    # Try to extract from AI content first
    domain_scores = {}

    # Fallback: calculate from session state
    if not domain_scores:
        # Physical domain
        physical_completed = sum(1 for task in st.session_state.physical_tasks_results if task.get('completed', False))
        physical_total = len(st.session_state.physical_tasks_results)
        physical_score = (physical_completed / physical_total * 100) if physical_total > 0 else 0

        # Linguistic domain
        linguistic_completed = sum(
            1 for task in st.session_state.linguistic_tasks_results if task.get('completed', False))
        linguistic_total = len(st.session_state.linguistic_tasks_results)
        linguistic_score = (linguistic_completed / linguistic_total * 100) if linguistic_total > 0 else 0

        # Cognitive domain
        cognitive_completed = sum(
            1 for task in st.session_state.cognitive_tasks_results if task.get('completed', False))
        cognitive_total = len(st.session_state.cognitive_tasks_results)
        cognitive_score = (cognitive_completed / cognitive_total * 100) if cognitive_total > 0 else 0

        domain_scores = {
            'physical': {'score': physical_score, 'expected': 80, 'status': get_status(physical_score, 80),
                         'percentile': get_percentile(physical_score)},
            'linguistic': {'score': linguistic_score, 'expected': 85, 'status': get_status(linguistic_score, 85),
                           'percentile': get_percentile(linguistic_score)},
            'cognitive': {'score': cognitive_score, 'expected': 75, 'status': get_status(cognitive_score, 75),
                          'percentile': get_percentile(cognitive_score)}
        }

    return domain_scores


def get_status(score, expected):
    """Determine performance status."""
    diff = score - expected
    if diff >= 10:
        return "Advanced"
    elif diff >= -10:
        return "On Track"
    else:
        return "Needs Support"


def get_percentile(score):
    """Calculate percentile."""
    if score >= 90:
        return 95
    elif score >= 80:
        return 75
    elif score >= 70:
        return 50
    elif score >= 60:
        return 25
    else:
        return 10


def determine_development_level(domain_scores, overall_score):
    """Determine overall development level."""
    avg_score = sum(data['score'] for data in domain_scores.values()) / len(domain_scores)

    if avg_score >= 85:
        return "Advanced"
    elif avg_score >= 70:
        return "On Track"
    else:
        return "Needs Support"


def parse_ai_sections(ai_content):
    """Parse AI content into sections."""
    sections = {}
    current_section = None
    content_lines = []

    for line in ai_content.split('\n'):
        if line.startswith('#'):
            if current_section:
                sections[current_section] = '\n'.join(content_lines)
            current_section = line.strip('#').strip()
            content_lines = []
        else:
            content_lines.append(line)

    if current_section:
        sections[current_section] = '\n'.join(content_lines)

    return sections


def extract_recommendations(ai_content, domain_scores):
    """Extract or generate recommendations."""
    # Try to parse from AI content, fallback to generated
    recommendations = []

    for domain, data in domain_scores.items():
        if data['score'] < 70:
            recommendations.append({
                'domain': domain.title(),
                'priority': 'High',
                'activity': f'Targeted {domain} development activities',
                'frequency': 'Daily, 15-20 minutes',
                'goal': f'Improve {domain} skills by 15-20 points over 3 months'
            })

    return recommendations[:3]  # Limit to top 3


def create_export_data(domain_scores, metadata):
    """Create comprehensive export data."""
    return {
        'assessment_date': datetime.now().isoformat(),
        'child_info': st.session_state.user_info,
        'domain_scores': domain_scores,
        'task_results': {
            'physical': st.session_state.physical_tasks_results,
            'linguistic': st.session_state.linguistic_tasks_results,
            'cognitive': st.session_state.cognitive_tasks_results
        },
        'metadata': metadata
    }


def generate_enhanced_ai_report_from_pdf(pdf_path):
    """Enhanced wrapper for AI report generation."""
    try:
        from utils.report_generator import AIReportGenerator  # Import your enhanced generator
        generator = AIReportGenerator()

        success, report_content, metadata = generator.process_pdf_to_ai_report(pdf_path)

        if success:
            report_path = generator.save_ai_report(
                report_content,
                st.session_state.user_info['child_name']
            )
            return report_path, report_content, metadata
        else:
            return None, None, {}

    except Exception as e:
        st.error(f"AI report generation failed: {str(e)}")
        return None, None, {}
# Helper functions for running tasks
def run_physical_task(task_id, task_function, task_name):
    """Execute a physical task and record results"""
    try:
        st.markdown(f"<h4 style='text-align: center;'>{task_name}</h4>", unsafe_allow_html=True)

        # Run the task
        result = task_function()

        # Process result
        if result:
            score = result.get('score', 0)
            completed = result.get('completed', False)

            # Store result
            task_result = {
                'task_id': task_id,
                'task_name': task_name,
                'score': score,
                'completed': completed,
                'timestamp': time.time(),
                'age_group': st.session_state.age_group
            }

            # Update or append result
            existing_idx = None
            for i, existing in enumerate(st.session_state.physical_tasks_results):
                if existing['task_id'] == task_id:
                    existing_idx = i
                    break

            if existing_idx is not None:
                st.session_state.physical_tasks_results[existing_idx] = task_result
            else:
                st.session_state.physical_tasks_results.append(task_result)

            # Show feedback
            if completed:
                st.success(f"Great job! Task completed successfully! Score: {score}")
            else:
                st.info(f"Good effort! Keep practicing. Score: {score}")

            return score
        else:
            st.error("Task could not be completed. Please try again.")
            return 0

    except Exception as e:
        st.error(f"Error running task: {str(e)}")
        return 0


def run_linguistic_task(task_id, task_function, task_name):
    """Execute a linguistic task and record results"""
    try:
        st.markdown(f"<h4 style='text-align: center;'>{task_name}</h4>", unsafe_allow_html=True)

        # Run the task
        result = task_function()

        # Process result
        if result:
            score = result.get('score', 0)
            completed = result.get('completed', False)

            # Store result
            task_result = {
                'task_id': task_id,
                'task_name': task_name,
                'score': score,
                'completed': completed,
                'timestamp': time.time(),
                'age_group': st.session_state.age_group
            }

            # Update or append result
            existing_idx = None
            for i, existing in enumerate(st.session_state.linguistic_tasks_results):
                if existing['task_id'] == task_id:
                    existing_idx = i
                    break

            if existing_idx is not None:
                st.session_state.linguistic_tasks_results[existing_idx] = task_result
            else:
                st.session_state.linguistic_tasks_results.append(task_result)

            # Show feedback
            if completed:
                st.success(f"Excellent communication! Task completed successfully! Score: {score}")
            else:
                st.info(f"Good attempt! Keep practicing speaking. Score: {score}")

            return score
        else:
            st.error("Task could not be completed. Please try again.")
            return 0

    except Exception as e:
        st.error(f"Error running task: {str(e)}")
        return 0


def process_intelligence_task(age_group, category, answer, task_name):
    """Process intelligence task results"""
    try:
        # Get the question data
        question_data = INTELLIGENCE_QUESTIONS.get(age_group, {}).get(category, {})

        # Determine if answer is correct (if there's a correct answer)
        is_correct = False
        if 'correct' in question_data:
            is_correct = (answer == question_data['correct'])

        # Calculate score (simplified scoring system)
        score = 100 if is_correct else 50  # Give partial credit for attempt

        # Create task result
        task_result = {
            'task_name': task_name,
            'category': category,
            'answer': answer,
            'correct_answer': question_data.get('correct', None),
            'is_correct': is_correct,
            'score': score,
            'completed': is_correct,  # Always completed if an answer was given
            'timestamp': time.time(),
            'age_group': age_group
        }

        # Store result
        st.session_state.cognitive_tasks_results.append(task_result)

        return score

    except Exception as e:
        st.error(f"Error processing intelligence task: {str(e)}")
        return 0

# Main application logic
def main():
    # Check current task state and route accordingly
    if st.session_state.age_group is None:
        select_age_group()
    elif st.session_state.current_task == 1:
        perform_physical_task()
    elif st.session_state.current_task == 2:
        perform_linguistic_task()
    elif st.session_state.current_task == 3:
        ask_intelligence_questions()
    elif st.session_state.current_task == 4:
        show_results()
    else:
        # Default back to age selection
        select_age_group()


if __name__ == "__main__":
    main()

