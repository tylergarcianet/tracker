from app import models, db


def run():
    db.create_all()

    admin = models.User(email="dummy@tylergarcia.net", username="dummy", password="dummypass")
    token = admin.generate_confirmation_token()
    admin.confirm(token)
    announcement = models.Ticket(tickettitle="Admin ticket", ticketrequest="some ticket details here. This ticket is only seen by admins", user_id=1)

    db.session.add(admin)
    db.session.add(announcement)
    db.session.commit()

    demo_user = models.User(email="demo_user@tylergarcia.net", username="demo_user", password="demopass")
    token = demo_user.generate_confirmation_token()
    demo_user.confirm(token)
    demo_ticket = models.Ticket(tickettitle="Demo Ticket", ticketrequest="this is an example of a user submitted ticket", user_id=2)
    closed_ticket = models.Ticket(tickettitle="Closed Ticket", ticketrequest="this is an example of a closed ticket", user_id=2, is_open=False)
    db.session.add(demo_user)
    db.session.add(demo_ticket)
    db.session.add(closed_ticket)

    all_fake_users = []
    for i in range(1, 6):
        fake_user = models.User(email="fake_user{}@fakeemail".format(str(i)), username="fake_user{}".format(str(i)), password="fakepass")
        ticket = models.Ticket(tickettitle="example ticket #{}".format(str(i)), ticketrequest="some ticket details here...", user_id=i + 2)
        db.session.add(fake_user)
        db.session.add(ticket)
        all_fake_users.append(fake_user)

    for i in range(6, 11):
        fake_user = models.User(email="fake_user{}@fakeemail".format(str(i)), username="fake_user{}".format(str(i)), password="fakepass")
        ticket = models.Ticket(tickettitle="example ticket #{}".format(str(i)), ticketrequest="some ticket details here...", user_id=i + 2 - 5)
        db.session.add(fake_user)
        db.session.add(ticket)
        all_fake_users.append(fake_user)

    db.session.commit()
