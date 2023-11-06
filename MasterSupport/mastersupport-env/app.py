from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

# Absolute path to the CSV file
csv_file_path = 'C:\\Users\\user\\Desktop\\MasterSupport\\mastersupport-env\\data\\tickets.csv'
status_csv_path = 'C:\\Users\\user\\Desktop\\MasterSupport\\mastersupport-env\\data\\status.csv'

@app.route('/')
def home():
    tickets = []
    statuses = []  # Initialize the statuses list
    next_ticket_id = 1  # Start with 1 if there are no tickets
    if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            tickets_list = list(csv_reader)
            if tickets_list:
                next_ticket_id = int(tickets_list[-1]['Ticket ID']) + 1
            tickets = tickets_list[-5:]  # Get the last 5 tickets
# Read statuses
    if os.path.exists(status_csv_path) and os.path.getsize(status_csv_path) > 0:
        with open(status_csv_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            statuses = list(csv_reader)  # Directly use the list of status dictionaries

    return render_template('home.html', tickets=tickets, next_ticket_id=next_ticket_id, statuses=statuses)

@app.route('/submit-ticket', methods=['POST'])
def submit_ticket():
    if request.method == 'POST':
        new_ticket = {
            'Ticket ID': request.form['ticket_id'],
            'Company Name': request.form['company_name'],
            'DOT Number': request.form['dot_number'],
            'Contact Name': request.form['contact_name'],
            'Phone Number': request.form['phone_number'],
            'Purpose': request.form['purpose'],
            'Description': request.form['description'],
            'Date': request.form['date'],
            'Representative': request.form['representative'],
            'Status': request.form['status']
        }
        
        fieldnames = ['Ticket ID', 'Company Name', 'DOT Number', 'Contact Name', 'Phone Number', 'Purpose', 'Description', 'Date', 'Representative', 'Status']
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # Write header if file is empty
                csv_writer.writeheader()
            csv_writer.writerow(new_ticket)
        return redirect('/')
    
@app.route('/record-status', methods=['GET', 'POST'])
def record_status():
    if request.method == 'POST':
        # Logic to record the new status or update the existing one
        current_name = request.form['name']
        current_status = request.form['status']
        current_time = request.form['time']
        current_date = request.form['date']
        current_location = request.form['location']  # Make sure to get the location from the form

        # Read the current statuses
        statuses = []
        if os.path.exists(status_csv_path) and os.path.getsize(status_csv_path) > 0:
            with open(status_csv_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                statuses = list(csv_reader)

        # Check if the employee already has a status recorded for the given date
        status_found = False
        for status in statuses:
            if status['Name'] == current_name and status['Date'] == current_date:
                status['Status'] = current_status  # Update the status
                status['Time'] = current_time  # Update the time
                status['Location'] = current_location  # Update the location
                status_found = True
                break

        # Write the updated statuses back to the CSV
        fieldnames = ['Name', 'Status', 'Location', 'Time', 'Date']
        with open(status_csv_path, mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(statuses)

        if not status_found:
            # If the status was not found for the given date, append the new status
            with open(status_csv_path, mode='a', newline='', encoding='utf-8') as file:
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
                csv_writer.writerow({
                    'Name': current_name,
                    'Status': current_status,
                    'Location': current_location,
                    'Time': current_time,
                    'Date': current_date
                })

        return redirect('/')
    # If it's a GET request, just render the status recording page
    return render_template('record_status.html')


@app.route('/all-tickets')
def all_tickets():
    tickets = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        tickets = list(reversed(list(csv_reader)))  # Reverse the list to show most recent first
    
    # Get filter values from the query string
    filter_values = {
        'Ticket ID': request.args.get('ticket_id'),
        'Company Name': request.args.get('company_name'),
        'DOT Number': request.args.get('dot_number'),
        'Contact Name': request.args.get('contact_name'),
        'Phone Number': request.args.get('phone_number'),
        'Purpose': request.args.get('purpose'),
        'Date': request.args.get('date'),
        'Representative': request.args.get('representative'),
        'Status': request.args.get('status'),
    }
    
    # Filter tickets based on the criteria
    if any(filter_values.values()):  # Check if any filter has been provided
        tickets = [ticket for ticket in tickets if all(
            ticket[key] == value or not value for key, value in filter_values.items()
        )]
    
    return render_template('all_tickets.html', tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)