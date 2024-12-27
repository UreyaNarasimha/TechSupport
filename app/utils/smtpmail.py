
import smtplib
import string
import random  # define the random module
from app.user.models.models import User
from app.utils.form_validations import password_validator

def generate_temp_password_and_check():
    S = 8  # number of characters in the string.
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = str(''.join(random.choices(alphabet, k=S)))
    if not password_validator(password):
        return generate_temp_password_and_check()
    return password


def send_mail_to_reset_password(to, user_name):
    
    gmail_user = 'techblog@gmail.com'
    gmail_password = '*********'
    sent_from = gmail_user

    password = generate_temp_password_and_check()
    subject = 'Forgot Password'
    body = "Hello " + f'{user_name}, ' + "\n\n" + \
           'Your account password with tech-blog has been changed and below are your login details.\n' +\
           "Email: " + f'{to}' + "\n" + \
           "Password: " + f'{password}' + "\n\n" + "Thanks,\nTech-Blog Group"

    email_text = f'Subject: {subject}' \
                 f'\n' \
                 f'\n' \
                 f'{body}'

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        # print("Email sent successfully!")
        return password
    except Exception as ex:
        print("Something went wrong….", ex)
        return "Error"


def mail_for_support_ticket(support_ticket_obj):
    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'
    sent_from = gmail_user

    subject = '[Tech-Blog] : Support Ticket '
    # subject = 'Support Ticket'
    user_name = User.query.filter_by(id=support_ticket_obj.u_id).first().name
    to = User.query.filter_by(id=support_ticket_obj.u_id).first().email

    if support_ticket_obj.status:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket is been raised with the following ticket id.\n' + \
               "Ticket Id: " + f'{support_ticket_obj.id}' + "\n" + \
               'We will resolve your issue at the earliest.\n' + \
               "\n\n" + "Thanks,\nTech-Blog Group"
    else:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket with ticket id ' + f'{support_ticket_obj.id}' + \
               'is resolved. Please check and feel free to contact us if you have any more further issues.\n' + \
               "\n\n" + "Thanks,\nTech-Blog Group"

    email_text = f'Subject: {subject}' \
                 f'\n' \
                 f'\n' \
                 f'{body}'

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        # print("Email sent successfully!")
        return
    except Exception as ex:
        print("Something went wrong….", ex)

def mail_for_updating_support_ticket(support_ticket_obj):
    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'
    sent_from = gmail_user

    subject = '[Tech-Blog] : Support Ticket '
    # subject = 'Support Ticket'
    user_name = User.query.filter_by(id=support_ticket_obj.u_id).first().name
    to = User.query.filter_by(id=support_ticket_obj.u_id).first().email

    if support_ticket_obj.status==True and support_ticket_obj.userdelete==False:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket is been raised with the following ticket id.\n' + \
               "Ticket Id: " + f'{support_ticket_obj.id}' + "\n" + \
               'has been updated successfully.\n' + \
               'Please  feel free to contact us if you have any more further issues.\n' + \
               "\n\n" +\
               "\n\n" + "Thanks,\nTech-Blog Group"

        email_text = f'Subject: {subject}' \
                     f'\n' \
                     f'\n' \
                     f'{body}'

        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            # print("Email sent successfully!")
            return
        except Exception as ex:
            print("Something went wrong….", ex)
    else:
        app.logger.info("Ticket closed succesfully")
        return jsonify(status=404,message="Ticket closed succesfully")


def mail_for_cancelling_support_ticket(support_ticket_obj):
    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'
    sent_from = gmail_user

    subject = '[Tech-Blog] : Support Ticket '
    # subject = 'Support Ticket'
    user_name = User.query.filter_by(id=support_ticket_obj.u_id).first().name
    to = User.query.filter_by(id=support_ticket_obj.u_id).first().email

    if support_ticket_obj.status==True and support_ticket_obj.userdelete==False:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket is been raised with the following ticket id.\n' + \
               "Ticket Id: " + f'{support_ticket_obj.id}' + "\n" + \
               'was cancelled successfully.\n' + \
               'Please  feel free to contact us if you have any more further issues.\n' + \
               "\n\n" + \
               "\n\n" + "Thanks,\nTech-Blog Group"

        email_text = f'Subject: {subject}' \
                     f'\n' \
                     f'\n' \
                     f'{body}'

        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            # print("Email sent successfully!")
            return
        except Exception as ex:
            print("Something went wrong….", ex)
    else:
        app.logger.info("Ticket already closed")
        return jsonify(status=404, message="Ticket already closed")


# # import smtplib
# # import secrets
# # import string
# # import re
# #
# #
# # def generate_temp_password_and_check():
# #     alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
# #     password = ''.join(secrets.choice(alphabet) for i in range(8))
# #     if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
# #                     password):
# #         # print("Generated Password is not satisfying")
# #         return generate_temp_password_and_check()
# #     print(password)
# #     # print("Generated Password is satisfying")
# #     return password
# #
# #
# # def send_mail_to_reset_password(to, body):
# #
# #     gmail_user = 'techblog.application@gmail.com'
# #     gmail_password = 'techblog@123'
# #
# #     password = generate_temp_password_and_check()
# #
# #     sent_from = gmail_user
# #     subject = 'Temp Password'
# #     body = "Hello " + f'{body} ' + 'your temporary password is ' + f'{password}'
# #
# #     email_text = f'Subject: {subject}' \
# #                  f'\n' \
# #                  f'\n' \
# #                  f'{body}'
# #
# #     try:
# #         smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# #         smtp_server.ehlo()
# #         smtp_server.login(gmail_user, gmail_password)
# #         smtp_server.sendmail(sent_from, to, email_text)
# #         smtp_server.close()
# #         # print("Email sent successfully!")
# #         return password
# #     except Exception as ex:
# #         print("Something went wrong….", ex)
# #         return "Error"
#
#
# import smtplib
# import string
# import random  # define the random module
# from app.utils.form_validations import password_validator
#
#
# def generate_temp_password_and_check():
#     S = 8  # number of characters in the string.
#     alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
#     password = str(''.join(random.choices(alphabet, k=S)))
#     if not password_validator(password):
#         # print("Generated Password is not satisfying")
#         print(password)
#         return generate_temp_password_and_check()
#     print(password)
#     # print("Generated Password is satisfying")
#     return password
#
#
# def send_mail_to_reset_password(to, body):
#
#     gmail_user = 'techblog.application@gmail.com'
#     gmail_password = 'techblog@123'
#
#     password = generate_temp_password_and_check()
#
#     sent_from = gmail_user
#     # subject = '[Tech-Blog] : Reset Password'
#     subject = 'Forgot Password'
#     body = "Hello " + f'{body}, ' + "\n\n\n" + \
#            'Your account password with tech-blog has been changed and below are your login details.\n' +\
#            "Email: " + f'{to}' + "\n" + \
#            "Password: " + f'{password}' + "\n\n" + "Thanks,\nTech-Blog Group"
#
#     email_text = f'Subject: {subject}' \
#                  f'\n' \
#                  f'\n' \
#                  f'{body}'
#
#     try:
#         smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         smtp_server.ehlo()
#         smtp_server.login(gmail_user, gmail_password)
#         smtp_server.sendmail(sent_from, to, email_text)
#         smtp_server.close()
#         # print("Email sent successfully!")
#         return password
#     except Exception as ex:
#         print("Something went wrong….", ex)
#         return "Error"