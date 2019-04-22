

def send_notification(notification_message):
    try:
        import notify2
    except ImportError:
        print('Desktop notification disabled. Run `pipenv install --dev`.')
    else:
        message_title = 'application {appname}'.format(appname=APP_NAME)
        notify2.init(message_title)
        notify2.Notification(message_title, notification_message).show()
