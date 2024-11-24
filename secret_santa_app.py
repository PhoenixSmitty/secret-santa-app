import streamlit as st
import pandas as pd
import random
import yagmail

# File to store participants' data
DATA_FILE = "participants.csv"

st.title("🎅 Secret Santa 🎄")
st.write("Welcome to the Secret Santa organizer! Participants can enter their details below.")

# Participant Input Form
with st.form("participant_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    wish_list = st.text_area("Wish List")
    immediate_family = st.text_area("Immediate Family Members (Comma-separated)")

    submitted = st.form_submit_button("Submit Your Details")
    if submitted:
        # Save participant data to file
        new_data = pd.DataFrame([{
            "First Name": first_name,
            "Last Name": last_name,
            "Email": email,
            "Wish List": wish_list,
            "Immediate Family": [x.strip() for x in immediate_family.split(",")]
        }])
        try:
            existing_data = pd.read_csv(DATA_FILE)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = new_data
        updated_data.to_csv(DATA_FILE, index=False)
        st.success("Details submitted successfully!")

# Organizer View: Display Participant Data and Assign Secret Santas
if st.checkbox("Show Organizer Controls"):
    try:
        participants = pd.read_csv(DATA_FILE)
        st.subheader("Current Participants")
        st.dataframe(participants)

        if st.button("Assign Secret Santas"):
            # Convert Immediate Family from string back to list
            participants["Immediate Family"] = participants["Immediate Family"].apply(eval)
            participant_list = participants.to_dict(orient="records")

            random.shuffle(participant_list)
            assignments = {}

            for giver in participant_list:
                eligible_receivers = [
                    r for r in participant_list
                    if r["First Name"] + " " + r["Last Name"] != giver["First Name"] + " " + giver["Last Name"]
                    and r["First Name"] + " " + r["Last Name"] not in giver["Immediate Family"]
                    and r["First Name"] + " " + r["Last Name"] not in assignments.values()
                ]
                if not eligible_receivers:
                    st.error("Failed to assign Secret Santas. Try again!")
                    break
                receiver = random.choice(eligible_receivers)
                assignments[giver["First Name"] + " " + giver["Last Name"]] = receiver["First Name"] + " " + receiver["Last Name"]

            if len(assignments) == len(participant_list):
                st.success("Secret Santas assigned successfully!")
                st.json(assignments)

                # Send Emails
                st.subheader("Send Emails")
                sender_email = st.text_input("Your Email Address")
                sender_password = st.text_input("Your Email Password", type="password")

                if st.button("Send Emails"):
                    try:
                        yag = yagmail.SMTP(user=sender_email, password=sender_password)
                        for giver_name, receiver_name in assignments.items():
                            giver = next(g for g in participant_list if g["First Name"] + " " + g["Last Name"] == giver_name)
                            receiver = next(r for r in participant_list if r["First Name"] + " " + r["Last Name"] == receiver_name)

                            subject = "Your Secret Santa Assignment 🎁"
                            body = f"""
                            Hi {giver_name},

                            You are the Secret Santa for {receiver_name}!
                            Here is their wish list:
                            {receiver["Wish List"]}

                            Happy gifting!

                            🎅 Secret Santa App
                            """
                            yag.send(to=giver["Email"], subject=subject, contents=body)

                        st.success("Emails sent successfully!")
                    except Exception as e:
                        st.error(f"Failed to send emails: {e}")
    except FileNotFoundError:
        st.warning("No participant data found. Please have participants submit their details first.")