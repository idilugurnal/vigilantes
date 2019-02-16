from datetime import datetime

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.mail import send_mail

from django.core.exceptions import ObjectDoesNotExist

from vigi2.models import Room, Coupon, Reservation, UserWrapper

import random, string


def searchRoom(request):
    """
    Get checkin, checkout, number of desired reserving room and room type from user using POST
    Render home.html
    :param request:
    :return: list of all rooms that satisfy the type
    """

        # Check if User is confirmed, if not logout and redirect
    if request.user.is_authenticated():
        try:
            user = UserWrapper.objects.get(user=request.user)
        except ObjectDoesNotExist:
            user = UserWrapper(user=request.user, type="Customer", phonenumber="", token="", confirm=True)
            user.save()

            # Give 3 dummy coupons to new user object
            c = Coupon()
            c.save()
            user.coupons.add(c)
            d = Coupon()
            d.save()
            user.coupons.add(d)
            e = Coupon()
            e.save()
            user.coupons.add(e)
            user.save()

        if not user.confirm:
            logout(request)
            return render(
                request,
                'login.html',
                {
                    'register': True,
                    'message': "Your account has not been confirmed.",
                }
            )


    checkin = request.POST.get("checkin", 0)
    checkout = request.POST.get("checkout", 0)
    number = request.POST.get("number", 0)
    roomtype = request.POST.get("roomtype", "King")
    rooms = None
    if checkin != 0:
        rooms = Room.objects.filter(type=roomtype)
    user = request.user
    if request.user.is_authenticated():
        user = UserWrapper.objects.get(user=request.user)
        print user.type
    return render(
        request,
        'home.html',
        {
            'user': user,
            'rooms': rooms,
            'checkin': checkin,
            'checkout': checkout,
            'number': number,
        }
    )


def reserve(request, roomid=0, checkin=0, checkout=0, number=0):
    """
    Get room with given roomid and Put in new Reservation object
     Render the reserve page
    :param request:
    :param roomid:
    :param checkin:
    :param checkout:
    :param number:
    :return:
    """

    # If user is not Login, redirect to Login
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    user = UserWrapper.objects.get(user=request.user)

    # Get other details and create new Reservation object
    roomid = int(roomid)
    checkin = datetime.strptime(checkin, '%Y-%m-%d')
    checkout = datetime.strptime(checkout, '%Y-%m-%d')
    number = int(number)
    room = Room.objects.get(id=roomid)
    reservation = Reservation(user=request.user, room=room, checkin=checkin, checkout=checkout,
                              number=number)
    room.empty = False
    room.save()
    reservation.save()

    return render(
        request,
        'reserve.html',
        {
            'user': user,
            'reservation': reservation,
            'total_price': reservation.room.price * reservation.number,
            'discounted_price': 0,
            'coupons': user.coupons.all(),
        }
    )


def approve(request):
    newstaffs = UserWrapper.objects.filter(type="Hotel Staff", confirm=False)
    return render(
        request,
        'approve.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'newstaffs': newstaffs,
        }
    )


def approve_user(request, id=0):
    staff = UserWrapper.objects.get(id=id)
    staff.confirm = True
    staff.save()
    newstaffs = UserWrapper.objects.filter(type="Hotel Staff", confirm=False)
    return render(
        request,
        'approve.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'newstaffs': newstaffs,
            'show': True,
            'message': 'Approve new hotel staff'
        }
    )


def deny_user(request, id=0):
    staff = UserWrapper.objects.get(id=id)
    staff.delete()

    newstaffs = UserWrapper.objects.filter(type="Hotel Staff", confirm=False)
    return render(
        request,
        'approve.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'newstaffs': newstaffs,
            'show': True,
            'message': 'Deny hotel staff'
        }
    )


def register(request):
    """
    Given username, password, email, phonenumer via POST
    Create new User object with dummy coupons
    :param request:
    :return:
    """

    def randomword(length):
        return ''.join(random.choice(string.lowercase) for i in range(length))

    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    email = request.POST.get("email", "")
    phonenumber = request.POST.get("phonenumber", "")
    type = request.POST.get("type", "Customer")
    if username != "" and password != "":

        # Create User object
        user = User.objects.create_user(username, email, password)

        # Create UserWrapper object with 1-1 relation to User object
        token = randomword(10)
        new_user = UserWrapper(user=user, type=type, phonenumber=phonenumber, token=token)
        new_user.save()

        if type == "Customer":
            send_mail(
                'Confirm your registeration with Vigilantese.com',
                'Hello,\n Please confirm your registeration with us by going to this link:\nhttp://wordmoment.com:8000/confirm/' + token,
                'root@wordmoment.com',
                [email],
                fail_silently=False,
            )

        # Give 3 dummy coupons to new user object
        c = Coupon()
        c.save()
        new_user.coupons.add(c)
        d = Coupon()
        d.save()
        new_user.coupons.add(d)
        e = Coupon()
        e.save()
        new_user.coupons.add(e)
        new_user.save()

        message = "Please confirm your email"
        if type == "Hotel Staff":
            message = "Please ask one of the old staff to confirm your account"
        elif type == "Customer":
            message = "Please confirm your email"

        # Render the same page with notification
        return render(
            request,
            'login.html',
            {
                'register': True,
                'message': message,
            }
        )
    else:
        return render(
            request,
            'register.html',
        )


def confirm(request, token=None):
    """
    Being called from user email, match token with DB
    Change the confirm status in DB
    :param request:
    :param token:
    :return:
    """
    if token is None:
        return

    user = UserWrapper.objects.get(token=token)
    user.token = None
    user.confirm = True
    user.save()

    return render(
        request,
        'login.html',
        {
            'register': True,
            'message': "Your email has been confirm",
        }
    )


def pay(request, reservationid=0):
    """
    Now, cll for changing reservation status only. Pay object not being created
    For future usage
    :param request:
    :param reservationid:
    :return:
    """
    card = int(request.POST.get("card", 0))
    csv = int(request.POST.get("csv", 0))
    name = request.POST.get("name", "")

    # Check card info here

    # If credit card info is valid
    if True:
        # Get reservation with the given id
        reservation = Reservation.objects.get(id=reservationid)
        # Change reservation to True
        reservation.done = True
        reservation.save()
        return mypage(request)


def mypage(request):
    """
    Return mypage details with his UserWrapper and all of his done reservation
    :param request:
    :return:
    """
    return render(
        request,
        'mypage.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'reservations': Reservation.objects.filter(user=request.user, done=True)
        }
    )


def delete(request, reservationid=0):
    """
    Remove Reservation of a given id
    :param request:
    :param reservationid:
    :return:
    """
    Reservation.objects.get(id=reservationid).delete()
    return mypage(request)


def edit_reservation(request, reservationid=0):
    """
    Edit a reservation of a given id
    :param request:
    :param reservationid:
    :return:
    """
    reservation = Reservation.objects.get(id=reservationid)

    checkin = request.POST.get("checkin", 0)
    checkout = request.POST.get("checkout", 0)
    number = int(request.POST.get("number", 0))
    if checkin != 0:
        checkin = datetime.strptime(checkin, '%Y-%m-%d')
        checkout = datetime.strptime(checkout, '%Y-%m-%d')

        reservation.checkin = checkin
        reservation.checkout = checkout
        reservation.number = number
        reservation.save()

        return mypage(request)

    return render(
        request,
        'edit_reservation.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'reservation': Reservation.objects.get(id=reservationid)
        }
    )


def apply_coupons(request, reservationid=0, couponid=0):
    """
    Apply Coupon with couponid to the Reservation with reservationid
    :param request:
    :param reservationid:
    :param couponid:
    :return:
    """

    user = UserWrapper.objects.get(user=request.user)
    coupon = Coupon.objects.get(id=couponid)

    # Put applied coupon object into Reservation
    reservation = Reservation.objects.get(id=reservationid)
    reservation.coupon = coupon
    reservation.save()

    # Remove applied coupon obj from User
    user.coupons.remove(coupon)
    user.save()

    return render(
        request,
        'reserve.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'reservation': reservation,
            'total_price': reservation.room.price * reservation.number,  # Total price before applying coupon
            'discounted_price': (reservation.room.price * reservation.number) * 0.8,  # Discounted price 80%
            'coupons': UserWrapper.objects.get(user=request.user).coupons.all(),  # All coupons belong to this user
        }
    )


def editroom(response, roomid):
    """
    Change room Infomation, room type, room price etc.
    :param response:
    :param roomid:
    """
    pass


def retrieverooms(request):
    """
    Get all rooms from the DB
    :param request:
    :return:
    """
    return render(
        request,
        'retrieve_rooms.html',
        {
            'user': UserWrapper.objects.get(user=request.user),
            'rooms': Room.objects.all(),
        }
    )
