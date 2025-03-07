import streamlit as st
import calendar
from datetime import datetime
import json
import os

# File to store event data
EVENTS_FILE = 'events_data.json'
#EVENTS_FILE = 'events_dataPRO.json'

# Function to load events from JSON file
def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to save events to JSON file
def save_events():
    with open(EVENTS_FILE, 'w') as f:
        json.dump(st.session_state['calendars'], f)

# Initialize session state for calendars and selected day
if 'calendars' not in st.session_state:
    st.session_state['calendars'] = load_events()  # Load events from file if available

if 'selected_day' not in st.session_state:
    st.session_state['selected_day'] = None

# Sidebar for calendar management
st.sidebar.header("Manage Calendars")

# Add a new calendar
calendar_name = st.sidebar.text_input("Enter new calendar name")
if st.sidebar.button("Add Calendar"):
    if calendar_name and calendar_name not in st.session_state['calendars']:
        st.session_state['calendars'][calendar_name] = {'events': []}
        save_events()  # Save events to file after adding a calendar
        st.sidebar.success(f"Calendar '{calendar_name}' added.")
    elif calendar_name in st.session_state['calendars']:
        st.sidebar.error("Calendar already exists.")
    else:
        st.sidebar.error("Please enter a valid name.")

# Select a calendar to view
if st.session_state['calendars']:
    selected_calendar = st.sidebar.selectbox("Select a calendar to view", list(st.session_state['calendars'].keys()))
else:
    selected_calendar = None

# Delete a calendar
if selected_calendar:
    if st.sidebar.button("Delete Calendar"):
        del st.session_state['calendars'][selected_calendar]
        save_events()  # Save events to file after deleting a calendar
        st.sidebar.success(f"Calendar '{selected_calendar}' deleted.")
        selected_calendar = None

# Main interface for viewing and interacting with the selected calendar
st.title("CampusFlow")

if selected_calendar:
    st.subheader(f"Viewing Calendar: {selected_calendar}")

    # Display current month's calendar with navigation
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if 'month_offset' not in st.session_state:
        st.session_state['month_offset'] = 0

    # Navigation for next/previous month
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Previous Month"):
            st.session_state['month_offset'] -= 1
    with col2:
        if st.button("Next Month"):
            st.session_state['month_offset'] += 1

    # Calculate the new month and year
    new_month = (current_month + st.session_state['month_offset'] - 1) % 12 + 1
    new_year = current_year + (current_month + st.session_state['month_offset'] - 1) // 12

    # Display the calendar for the selected month
    st.write(f"### {calendar.month_name[new_month]} {new_year}")

    # Generate the calendar grid using HTML and CSS
    cal = calendar.Calendar(firstweekday=6)  # Start with Sunday
    month_days = cal.monthdayscalendar(new_year, new_month)

    # HTML table to represent the calendar grid
    html_calendar = f"""
    <style>
        .calendar-grid {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            text-align: center;
            font-family: Arial, sans-serif;
            padding: 10px;
        }}
        .calendar-grid .day-name {{
            font-weight: bold;
            background-color: #00165a;
            border-radius: 5px;
            padding: 5px;
        }}
        .calendar-grid .day {{
            padding: 10px;
            background-color: ;
            border-radius: 5px;
            cursor: pointer;
            position: relative;
        }}
        .calendar-grid .day:hover {{
            background-color: #00165a;
        }}
        .calendar-grid .day.event {{
            background-color: #94a0ff;
            font-weight: bold;
            font-color: #94a0ff;
        }}
        .tooltip {{
            visibility: hidden;
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #f9f9f9;
            color: black;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            width: max-content;
            z-index: 100;
        }}
        .calendar-grid .day:hover .tooltip {{
            visibility: visible;
        }}
    </style>
    <div class="calendar-grid">
        <div class="day-name">Sun</div>
        <div class="day-name">Mon</div>
        <div class="day-name">Tue</div>
        <div class="day-name">Wed</div>
        <div class="day-name">Thu</div>
        <div class="day-name">Fri</div>
        <div class="day-name">Sat</div>
    """

    # Fill the calendar with days and events
    for week in month_days:
        for day in week:
            if day == 0:
                html_calendar += f'<div class="day"></div>'  # Empty cell for days outside the month
            else:
                # Check if the day has any events
                events = [event for event in st.session_state['calendars'][selected_calendar]['events'] if datetime.fromisoformat(event['date']).month == new_month and datetime.fromisoformat(event['date']).day == day]
                event_class = "event" if events else ""
                # Only add tooltip if there are events
                if events:
                    event_tooltip = "<br>".join([event['description'] for event in events])
                    html_calendar += f'<div class="day {event_class}">{day}<div class="tooltip">{event_tooltip}</div></div>'
                else:
                    html_calendar += f'<div class="day">{day}</div>'

    html_calendar += "</div>"

    st.markdown(html_calendar, unsafe_allow_html=True)

    # Add events to the selected month
    event_date = st.date_input("Select a date to add an event", min_value=datetime(new_year, new_month, 1))

    if 'event_time' not in st.session_state:
        st.session_state['event_time'] = datetime.now().time()

    # Time input for the event
    event_time = st.time_input("Select a time for the event", value=st.session_state['event_time'])

    # Update session state when time changes
    if event_time != st.session_state['event_time']:
        st.session_state['event_time'] = event_time

    event_description = st.text_input("Enter description")

    # Classify as event or goal
    entry_type = st.radio("Classify this as:", ("Event", "Goal"))
    hours_per_week = None
    if entry_type == "Goal":
        hours_per_week = st.number_input("How many hours per week must be spent on this goal?", min_value=1, step=1)

    if st.button("Add Entry"):
        if event_description:
            # Combine the selected date and time into a datetime object
            event_datetime = datetime.combine(event_date, st.session_state['event_time'])
            event = {
                "date": event_datetime.isoformat(),
                "description": event_description,
                "type": entry_type,
            }
            if entry_type == "Goal":
                event["hours_per_week"] = hours_per_week

            st.session_state['calendars'][selected_calendar]['events'].append(event)
            save_events()  # Save events to file after adding
            st.success(f"{entry_type} added!")

            # Clear inputs after adding an event
            st.session_state['event_time'] = datetime.now().time()
            st.session_state['selected_day'] = None
        else:
            st.error("Please enter a description.")

    # Display events for the selected month with delete functionality
    st.subheader("Entries for this Month:")
    entries_this_month = [
        (i, event) for i, event in enumerate(st.session_state['calendars'][selected_calendar]['events']) 
        if datetime.fromisoformat(event['date']).month == new_month and datetime.fromisoformat(event['date']).year == new_year
    ]

    if entries_this_month:
        for index, event in entries_this_month:
            event_datetime = datetime.fromisoformat(event['date'])
            entry_info = f"**{event_datetime.strftime('%B %d, %Y %I:%M %p')}**: {event['description']} ({event['type']})"
            if event['type'] == "Goal":
                entry_info += f" - {event['hours_per_week']} hours/week"

            col1, col2 = st.columns([3, 1])  # Create two columns for displaying the entry and the delete button
            with col1:
                st.write(entry_info)
            with col2:
                if st.button("Delete", key=f"delete_{index}"):
                    # Remove the entry from the in-memory state
                    del st.session_state['calendars'][selected_calendar]['events'][index]
                    save_events()  # Save updated entries to the JSON file
                    st.experimental_rerun()  # Refresh the app
    else:
        st.write("No entries for this month.")

else:
    st.info("Please add or select a calendar to view.")
