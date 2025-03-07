
import json
import datetime

def generate_entries_with_strict_limits(goal, start_date, deadline, entries_per_week, weekday_start, weekday_end, saturday_start, saturday_end):
    entries = []
    deadline = datetime.datetime.fromisoformat(deadline)
    current_date = datetime.datetime.fromisoformat(start_date).replace(hour=weekday_start, minute=0, second=0, microsecond=0)
    week_entries_count = 0
    entry_count = 1
    entries_per_day = {}

    while current_date <= deadline:
        day_str = current_date.date().isoformat()
        is_weekday = current_date.weekday() < 5  # Monday-Friday
        is_saturday = current_date.weekday() == 5  # Saturday

        # Initialize daily count if not already set
        if day_str not in entries_per_day:
            entries_per_day[day_str] = 0

        # Schedule entries while respecting daily and weekly limits
        if (is_weekday and weekday_start <= current_date.hour < weekday_end) or (is_saturday and saturday_start <= current_date.hour < saturday_end):
            if entries_per_day[day_str] < 3 and week_entries_count < entries_per_week:
                entries.append({
                    "date": current_date.isoformat(),
                    "description": f"{goal}_{entry_count}",
                    "type": "Sub-Goal"
                })
                entries_per_day[day_str] += 1
                week_entries_count += 1
                entry_count += 1

        # Move to the next time slot or day
        current_date += datetime.timedelta(hours=1)
        if current_date.hour >= 24:  # Move to next day
            current_date += datetime.timedelta(days=1)
            current_date = current_date.replace(hour=weekday_start if is_weekday else saturday_start)
            if current_date.weekday() == 0:  # Reset weekly count on Monday
                week_entries_count = 0

    return entries

def populate_entries_strict_daily_limit(data, weekday_start, weekday_end, saturday_start, saturday_end):
    updated_data = data.copy()
    for section, content in updated_data.items():
        if "events" in content:
            existing_events = content["events"]
            new_events = []
            for event in existing_events:
                if event["type"] == "Goal":
                    goal_name = event["description"]
                    start_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Assume today
                    deadline = event["date"]
                    entries_per_week = event["hours_per_week"]

                    # Generate sub-goals with strict daily limits
                    sub_goals = generate_entries_with_strict_limits(
                        goal=goal_name,
                        start_date=start_date,
                        deadline=deadline,
                        entries_per_week=entries_per_week,
                        weekday_start=weekday_start,
                        weekday_end=weekday_end,
                        saturday_start=saturday_start,
                        saturday_end=saturday_end
                    )
                    new_events.extend(sub_goals)
            # Add sub-goal events to the section
            updated_data[section]["events"].extend(new_events)
    return updated_data

if __name__ == "__main__":
    # Load input JSON file
    with open("events_data.json", "r") as file:
        data = json.load(file)

    # Process the data
    updated_data = populate_entries_strict_daily_limit(
        data,
        weekday_start=16,
        weekday_end=22,
        saturday_start=10,
        saturday_end=16
    )

    # Write the processed data to a new file
    with open("events_dataPRO.json", "w") as file:
        json.dump(updated_data, file, indent=4)

    print("Processing complete. Output saved to 'events_dataPRO.json'.")
