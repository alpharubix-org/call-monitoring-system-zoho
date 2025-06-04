import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import datetime
import db
load_dotenv(override=True)

def get_call_history(access_token,smtp):
    sales_Manager_names = { #this list holds all the  sales manager names
    'Amare Gowda':"support23@meramerchant.com",
    'Ayush Dingane':"support14@meramerchant.com",
    'Digamber Pandey':"support17@meramerchant.com",
    'Pallavi Gattu':"support29@meramerchant.com",
    'Honnappa Dinni':"support25@meramerchant.com",
    'Kavya K B' :"support26@meramerchant.com",
    'Sandip Kumar Jena':"support13@meramerchant.com",
    'Sonu Sathyan':"support21@meramerchant.com"}

    for sm_name in sales_Manager_names:
        url = f"https://crm.zoho.com/crm/v2/Calls/search?criteria=(Owner:equals:{sm_name})and(Call_Status:equals:Overdue)&per_page=200&page=1"
        headers = {
            "Authorization":f"Zoho-oauthtoken {access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            # if the call is overdue triger a mail notification to the sales manager
           
            if response.status_code == 204:
                print("No calls found for this sales_manager")
                continue
            data = response.json().get('data')
            print('Total call count is',len(data))
            overdue_call_count = 0# holds the number of overdue calls per sales manager
            collection = db.get_collection()
            day_warning_count = 0
            two_day_warning_count = 0
            three_day_warning_count = 0
            more_than_three_day_warning_count = 0

            for call in data:
                created_time = call.get('Created_Time') #call created time Created_Time
                formated_time =  datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z').date()
                date_now = datetime.datetime.now().date()
                delay_count =  date_now - formated_time #calculate the delay count days
                if delay_count.days > 3:
                    more_than_three_day_warning_count+=1
                    continue
                if delay_count.days == 0:
                    continue
                else:
                    if delay_count.days==1:
                       #check if the warning count is created or not if not create a warning count
                        if collection.find_one({'call_id':call.get('id')}) is None:#create a warning count 
                            collection.insert_one({"sales_manager":sm_name,"lead_name":(call.get('What_Id').get('name')),"call_id":call.get('id'),"Warning_count":1,"last_modified_date":datetime.datetime.now().strftime('%Y-%m-%d')})
                            send_overdue_email_to_sales_manager(manager_name=sm_name,sales_manger_email=sales_Manager_names[sm_name],overdue_call_id=call.get('id'),smtp=smtp)
                            day_warning_count+=1
                            print("call overdue notification send database created")
                        else:
                           print("mail already sent for  1 day warning")
                    elif delay_count.days==2:
                        #check if the email is already sent today or not
                        warning_doc = collection.find_one({'call_id':call.get('id')})
                        get_last_up = warning_doc.get('last_modified_date') #fetch the last modified date
                        if get_last_up == datetime.datetime.now().strftime('%Y-%m-%d'):
                            print("Email already sent for today")
                        else:
                            collection.update_one(
                                        {'call_id': call.get('id')},
                                        {
                                            '$inc': {"Warning_count": 1},
                                            '$set': {"last_modified_date": datetime.datetime.now().strftime('%Y-%m-%d')}
                                        }
                                    )
                            send_overdue_email_to_manager(lead_name=call.get('Last_Name'),sales_rep_name=sales_Manager_names[sm_name],smtp=smtp)
                            two_day_warning_count+=1
                            print("call overdue notification  send to manager database updated")
                    elif delay_count.days==3:
                        warning_doc = collection.find_one({'call_id':call.get('id')})
                        get_last_up = warning_doc.get('last_modified_date') #fetch the last modified date
                        if get_last_up == datetime.datetime.now().strftime('%Y-%m-%d'): 
                            print("Email already sent for today")
                        else:
                            collection.update_one(
                                {'call_id': call.get('id')},
                                {
                                    '$inc': {"Warning_count": 1},
                                    '$set': {"last_modified_date": datetime.datetime.now().strftime('%Y-%m-%d')}
                                }
                            )
                            send_overdue_email_to_ceo(lead_name=call.get('Last_Name'),sales_rep_name=sales_Manager_names[sm_name],smtp=smtp)
                            three_day_warning_count+=1
                            print("call overdue notification  send to manager database updated")                  
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")
        print("onedaydelayedcall",day_warning_count)
        print("twodaydelayedcall",two_day_warning_count)
        print("threedaydelayedcall",three_day_warning_count)
        print("fourdaydelayedcall",more_than_three_day_warning_count)    

def send_overdue_email_to_sales_manager(manager_name,sales_manger_email ,overdue_call_id,smtp,sender_name="call-monitoring-system",):
    subject = "Test mail Action Required: Overdue Calls Alert"
    html_content = f"""
    <p>Dear {manager_name},</p>
    <p>Your call is overdued for the call id <strong>{overdue_call_id}</strong>. Please take action immediately.</p>
    """
    
    # Build the message
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <techmgr@meramerchant.com>"
    msg['To'] = sales_manger_email 
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    # Send using Zoho SMTP
    try:
        smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)

def create_smtp_connection():
    try:
            smtp = smtplib.SMTP('smtp.zoho.com', 587, timeout=10) 
            smtp.starttls()
            app_password = os.getenv("APP_PASSWORD").strip()
            smtp.login('techmgr@meramerchant.com', app_password)
            print("SMTP connection created successfully.")
            return smtp
    except Exception as e:
        print("Error creating SMTP connection:", e)
        return None        

def send_overdue_email_to_manager( lead_name, sales_rep_name, smtp, sender_name="call-monitoring-system"):
    subject = "Test mail Action Required: Overdue Calls Alert"
    html_content = f"""
    <p>Dear manager ,</p>
    <p>The lead for call name <strong>{lead_name}</strong> is pending for 2 days and is assigned to {sales_rep_name}. Please take immediate action to follow up with the lead.</p>
    """
    
    # Build the message
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <techmgr@meramerchant.com>"
    msg['To'] = 'supportmgr@meramerchant.com'
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    # Send using Zoho SMTP
    try:
        smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)


def send_overdue_email_to_ceo( lead_name, sales_rep_name, smtp, sender_name="call-monitoring-system"):
    subject = "Test mail Action Required: Overdue Calls Alert"
    html_content = f"""
    <p>Dear manager ,</p>
    <p>The lead for call name <strong>{lead_name}</strong> is pending for 3 days and is assigned to {sales_rep_name}. Please take immediate action to follow up with the lead.</p>
    """
    
    # Build the message
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <techmgr@meramerchant.com>"
    msg['To'] = 'prathap@meramerchant.com'
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    # Send using Zoho SMTP
    try:
        smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)
